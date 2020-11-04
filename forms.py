from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import InputRequired, Email


class RegisterUser(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])

    password = PasswordField("Password", validators=[InputRequired()])

    email = StringField("Email", validators=[Email(), InputRequired()])

    first_name = StringField("First Name", validators=[InputRequired()])

    last_name = StringField("Last Name", validators=[InputRequired()])


class LogInUser(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])

    password = PasswordField("Password", validators=[InputRequired()])


class FeedbackForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired()])

    content = TextAreaField("Feedback", validators=[InputRequired()])
