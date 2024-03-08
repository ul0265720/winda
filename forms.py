from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL, NumberRange
from flask_ckeditor import CKEditorField
from wtforms import DateField


# WTForm for creating a blog post
class CreatePostForm(FlaskForm):
    title = StringField("Tytuł", validators=[DataRequired()])
    subtitle = StringField("Temat", validators=[DataRequired()])
    img_url = StringField("Zdjęcie", validators=[URL()])
    body = CKEditorField("Treść", validators=[DataRequired()])
    submit = SubmitField("Opublikuj")
    

# Create a form to register new users
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Hasło", validators=[DataRequired()])
    name = StringField("Imię", validators=[DataRequired()])
    submit = SubmitField("Zarejestruj")


# Create a form to login existing users
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Hasło", validators=[DataRequired()])
    submit = SubmitField("Zaloguj")


# Create a form to add comments
class CommentForm(FlaskForm):
    comment_text = CKEditorField("Komentarz", validators=[DataRequired()])
    submit = SubmitField("Dodaj komentarz")
    rating = IntegerField('Ocena', validators=[NumberRange(min=1, max=5)])



class EditProfileForm(FlaskForm):
    name = StringField('Imię')
    email = StringField('Email')
    password = PasswordField('Hasło')
    submit = SubmitField('Zapisz zmiany')

class AddUserForm(FlaskForm):
    login = StringField("login",validators=[DataRequired()])
    password = PasswordField("password",[DataRequired()])
    name= StringField("name",[DataRequired()])
    last_name= StringField("last name",[DataRequired()])
    city = StringField("city",[DataRequired()])
    
    postal_code = StringField("postal code",[DataRequired()])
    street = StringField("street",[DataRequired()])
    street_number = IntegerField("street number",[DataRequired()])
    flat_number = IntegerField("flat number",[DataRequired()])
    pesel = StringField("pesel",[DataRequired()])
    birth_date = DateField("birth date",[DataRequired()])
    email = StringField("email",[DataRequired()])

class SearchForm(FlaskForm):
    query = StringField('Query', validators=[DataRequired()])
    submit = SubmitField('Search')
    search_category = SelectField('Search Category', choices=[
        ('name', 'Login'),
        ('email', 'E-mail'),
        ('last_name', 'Imię i nazwisko')
    ], validators=[DataRequired()])



   # sex = db.Column(db.String(10))

