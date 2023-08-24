from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import InputRequired, Length, ValidationError, Email
from models import User

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()], render_kw={"placeholder": "Email"})
    username = StringField("Username", validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField("Password", validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")
    
    def validate_username(self, username):
        existing_user_name = User.query.filter_by(username=username.data).first()
        if existing_user_name:
            raise ValidationError("That username already exists. Please choose a different username.")

    
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField("Password", validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Log In")
    
class AddToddlerForm(FlaskForm):
    name = StringField("Toddler Name", validators=[InputRequired()], render_kw={"placeholder": "Toddler Name"})
    age = IntegerField("Toddler Age(In Months)", validators=[InputRequired()], render_kw={"placeholder" : "e.g., 24"})
    learned_words = StringField("Already Learned Words", render_kw={"placeholder" : "e.g., dog, cat, hi"})
    submit = SubmitField('Add Toddler')
