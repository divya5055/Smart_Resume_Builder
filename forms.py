from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length


# Register Form
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4)])
    submit = SubmitField('Register')


# Login Form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


# Resume Builder Form (we will use later)
class ResumeForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email')
    phone = StringField('Phone')
    skills = TextAreaField('Skills')
    education = TextAreaField('Education')
    experience = TextAreaField('Experience')
    summary = TextAreaField('Summary')
    submit = SubmitField('Generate Resume')


# Resume Analyzer Form
class AnalyzerForm(FlaskForm):
    resume_text = TextAreaField('Paste Resume Text', validators=[DataRequired()])
    job_description = TextAreaField('Job Description', validators=[DataRequired()])
    submit = SubmitField('Analyze')