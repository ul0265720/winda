from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, SubmitField
from wtforms.validators import DataRequired, URL, NumberRange
from flask_ckeditor import CKEditorField


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