from datetime import date
from flask import Flask, abort, render_template, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from flask_login import login_required
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from urllib.parse import quote, unquote
from sqlalchemy import func
import time



# Import your forms from the forms.py
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm, EditProfileForm, AddUserForm, SearchForm



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap5(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# For adding profile images to the comment section
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy()
migrate = Migrate(app, db)
db.init_app(app)


# CONFIGURE TABLES
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Create reference to the User object. The "posts" refers to the posts property in the User class.
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    # Parent relationship to the comments
    comments = relationship("Comment", back_populates="parent_post")


# Create a User table for all your registered users
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(20),unique =True)
    password = db.Column(db.String(100))
    name= db.Column(db.String(30))
    last_name= db.Column(db.String(30))
    city = db.Column(db.String(30))
    postal_code = db.Column(db.String(6))
    street = db.Column(db.String(20))
    street_number = db.Column(db.Integer)
    flat_number = db.Column(db.Integer)
    pesel = db.Column(db.String(30), unique = True)
    birth_date = db.Column(db.Date)
 #   sex = db.Column(db.String(10))
    email = db.Column(db.String(100), unique=True)
    
    posts = relationship("BlogPost", back_populates="author")
    # Parent relationship: "comment_author" refers to the comment_author property in the Comment class.
    comments = relationship("Comment", back_populates="comment_author")


# Create a table for the comments on the blog posts
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")
    # Child Relationship to the BlogPosts
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")



with app.app_context():
    db.create_all()


from flask_login import current_user, login_required

# Modify the admin_only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the user is authenticated
        if not current_user.is_authenticated:
            # Redirect the user to the login page if not authenticated
            return redirect(url_for('login'))

        # Check if the user is an admin
        if current_user.id != 1:
            # Return a 403 Forbidden error if not an admin
            return abort(403)

        # Otherwise, continue with the route function
        return f(*args, **kwargs)

    return decorated_function


# Register new users into the User database
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        # Check if user email is already present in the database.
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            # User already exists
            flash("Taki e-mail istnieje, zaloguj się!")
            return redirect(url_for('login'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        # This line will authenticate the user with Flask-Login
        login_user(new_user)
        return redirect(url_for("get_all_posts"))
    return render_template("register.html", form=form, current_user=current_user)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        # Note, email in db is unique so will only have one result.
        user = result.scalar()
        # Email doesn't exist
        if not user:
            flash("E-mail nie istnieje, spróbuj ponownie.")
            return redirect(url_for('login'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            session['login_attempts'] = session.get('login_attempts', 0) + 1
            flash('Hasło niepoprawne, spróbuj ponownie.')
            
            # Check if login attempts exceed the limit (3)
            if session['login_attempts'] >= 3:
                session.pop('login_attempts', None)  # Reset login attempts
                flash('Your account has been temporarily blocked due to multiple failed login attempts.', 'error')

                time.sleep(5)

                return redirect(url_for('login'))
            
            return redirect(url_for('login'))
        else:
            login_user(user)
            session['login_attempts'] = 0  # Reset login attempts upon successful login
            return redirect(url_for('get_all_posts'))

    return render_template("login.html", form=form, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts, current_user=current_user)


# Add a POST method to be able to post comments
@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    # Add the CommentForm to the route
    comment_form = CommentForm()
    # Only allow logged-in users to comment on posts
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Musisz być zalogowany aby móc dodać komentarz.")
            return redirect(url_for("login"))

        new_comment = Comment(
            text=comment_form.comment_text.data,
            comment_author=current_user,
            parent_post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()
    return render_template("post.html", post=requested_post, current_user=current_user, form=comment_form)


# Use a decorator to ensure only logged-in users can create new posts
@app.route("/new-post", methods=["GET", "POST"])
@login_required
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form, current_user=current_user)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)

    # Dodaj warunek sprawdzający, czy aktualny użytkownik jest autorem posta
    if current_user.is_authenticated and post.author.id == current_user.id:
        edit_form = CreatePostForm(
            title=post.title,
            subtitle=post.subtitle,
            img_url=post.img_url,
            author=post.author,
            body=post.body
        )
        if edit_form.validate_on_submit():
            post.title = edit_form.title.data
            post.subtitle = edit_form.subtitle.data
            post.img_url = edit_form.img_url.data
            post.author = current_user
            post.body = edit_form.body.data
            db.session.commit()
            return redirect(url_for("show_post", post_id=post.id))
        return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user)
    else:
        # Jeśli aktualny użytkownik nie jest autorem posta, przekieruj lub obsłuż błąd
        flash("Nie masz urpawnień do edycji tego postu")
        return redirect(url_for("show_post", post_id=post.id))


# Use a decorator so only an admin user can delete a post
@app.route("/delete/<int:post_id>")
@login_required
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html", current_user=current_user)


@app.route("/contact")
def contact():
    return render_template("contact.html", current_user=current_user)



@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    form = EditProfileForm()

    if request.method == 'POST' and form.validate_on_submit():
        # Pobierz użytkownika z bazy danych
        user = User.query.get(current_user.id)

        # Zaktualizuj dane użytkownika z formularza
        user.name = form.name.data
        user.email = form.email.data
        user.password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        
        # ... inne pola profilu

        # Zapisz zmiany w bazie danych
        db.session.commit()

        flash('Profil zaktualizowany pomyślnie', 'success')
        return redirect(url_for('edit_profile'))

    return render_template('edit-profile.html', form=form, current_user=current_user)

@app.route('/adduser',methods=['GET', 'POST'])
@admin_only
def add_user():
    form = AddUserForm()

    if form.validate_on_submit():

        result = db.session.execute(db.select(User).where(User.email == form.email.data))
        user = result.scalar()
        if user:
            # User already exists
            flash("Taki e-mail istnieje, zaloguj się!")
            return redirect(url_for('add_user'))
        
        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )

        new_user = User(
            login = form.login.data, 
            password=hash_and_salted_password,
            name=form.name.data,
            last_name= form.last_name.data,
            city = form.city.data,
            postal_code = form.postal_code.data,
            street = form.street.data,
            street_number = form.street_number.data,
            flat_number = form.flat_number.data,
            pesel = form.pesel.data,
            birth_date = form.birth_date.data,
            email=form.email.data,
        )

        db.session.add(new_user)
        db.session.commit()
    return render_template('add_user.html', form=form)

####
from sqlalchemy import or_

@app.route('/users_and_search')
@admin_only
def user_search():
    search_form = SearchForm()
    query = request.args.get('query', '')
    category = search_form.search_category.data

    if category == 'login':
        users = User.query.filter(User.login.ilike(f'%{query}%')).all()
    elif category == 'email':
        users = User.query.filter(User.email.ilike(f'%{query}%')).all()
    elif category == 'last_name':
        users = User.query.filter(func.concat(User.name,' ', User.last_name).ilike(f'%{query}%')).all()

    users = User.query.filter(User.name.ilike(f'%{query}%')).all()
    return render_template("users_and_search.html", search_form=search_form, users=users)

###
#
#####
@app.route('/user/<int:user_id>')
@admin_only
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user_profile.html', user=user)


@app.route('/userd/<int:user_id>')
@admin_only
def user_delete(user_id):
    user = User.query.get_or_404(user_id)
    if user_id != 1:
        try:
            db.session.delete(user)
            db.session.commit()
            flash("jest git","error")  # Indicate successful deletion
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            db.session.rollback()  # Rollback the transaction in case of error
            flash("niejest git","error")  # Indicate deletion failure
    else:
        db.session.rollback()
    flash("admin","error")

    return render_template("users_and_search.html")

if __name__ == "__main__":

    app.run(debug=True, port=5001)
