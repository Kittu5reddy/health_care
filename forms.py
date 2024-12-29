from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, BooleanField, SubmitField,IntegerField,FileField,SelectField,TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional   

class SignupForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=2, max=50)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message="Passwords must match")
    ])
    terms = BooleanField('I agree to the terms of service', validators=[DataRequired()])
    isDoctor = BooleanField('I am a doctor')
    submit = SubmitField('Register')
    
    
    

class DoctorProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    specialization = StringField('Specialization', validators=[DataRequired()])
    experience = IntegerField('Experience (in years)', validators=[DataRequired()])
    qualifications = StringField('Qualifications', validators=[DataRequired()])
    contact_number = StringField('Contact Number', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    clinic_hospital = StringField('Clinic/Hospital Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[DataRequired()])
    submit = SubmitField('Submit')
   
    
    
    
    
    
class PatientProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[DataRequired()])
    blood_group = StringField('Blood Group', validators=[DataRequired()])
    contact_number = StringField('Contact Number', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    address = StringField('Address', validators=[DataRequired()])
    medical_history = TextAreaField('Medical History', validators=[Optional()])
    profile_photo = FileField('Profile Picture')
    submit = SubmitField('Submit')