from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, BooleanField, SubmitField,IntegerField,FileField,SelectField,TextAreaField,TelField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional,Regexp
from flask_wtf.file import FileAllowed, FileField  

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
    
    
class ReportProblemForm(FlaskForm):
    name = StringField(
        "Full Name",
        validators=[DataRequired(message="Full Name is required")],
        render_kw={"class": "form-control", "placeholder": "Enter your full name"},
    )
    email = EmailField(
        "Email Address",
        validators=[
            DataRequired(message="Email is required"),
            Email(message="Invalid email address"),
        ],
        render_kw={"class": "form-control", "placeholder": "Enter your email"},
    )
    contact = TelField(
        "Contact Number",
        validators=[
            DataRequired(message="Contact number is required"),
            Regexp(r"^\d{10}$", message="Enter a valid 10-digit number"),
        ],
        render_kw={"class": "form-control", "placeholder": "Enter your contact number"},
    )
    title = StringField(
        "Problem Title",
        validators=[DataRequired(message="Problem Title is required")],
        render_kw={"class": "form-control", "placeholder": "Enter the problem title"},
    )
    description = TextAreaField(
        "Problem Description",
        validators=[
            DataRequired(message="Problem description is required"),
            Length(min=10, message="Description must be at least 10 characters long"),
        ],
        render_kw={"class": "form-control", "rows": 3, "placeholder": "Describe your problem in detail"},
    )
    # files = FileField(
    #     "Attach Files",
    #     validators=[
    #         FileAllowed(["jpg", "jpeg", "png", "pdf", "doc", "docx"], "Invalid file format"),
    #     ],
    #     render_kw={"class": "form-control", "multiple": True},
    # )
    submit = SubmitField("Submit", render_kw={"class": "btn btn-primary"})