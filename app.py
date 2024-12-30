#imports
from flask import Flask,render_template,request,url_for,flash,redirect,session
from flask_session import Session
from flask_bcrypt import Bcrypt




#database
from flask_pymongo import PyMongo
from api_keys import mongodb

#Form imports
from forms import SignupForm,DoctorProfileForm,PatientProfileForm,ReportProblemForm



#oAuth
from authlib.integrations.flask_client import OAuth
from api_keys import google_keys
import random
import string


 
#app config
app=Flask(__name__)
app.config['MONGO_URI'] = mongodb['url']
mongo = PyMongo(app)
bycrypt = Bcrypt(app)

from api_keys import SECRET_KEY

app.config['SECRET_KEY'] = SECRET_KEY 
#app
app.config['GOOGLE_CLIENT_ID'] = google_keys['client_id']
app.config['GOOGLE_CLIENT_SECRET'] = google_keys['client_secret']
app.config['GOOGLE_DISCOVERY_URL'] = 'https://accounts.google.com/.well-known/openid-configuration'




#session config
app.config['SESSION_TYPE'] = 'mongodb'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_MONGODB'] = mongo.cx
app.config['SESSION_MONGODB_DB'] = 'health_care'
app.config['SESSION_MONGODB_COLLECT'] = 'sessions'

Session(app)


# Initialize OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    server_metadata_url=app.config['GOOGLE_DISCOVERY_URL'],
    client_kwargs={
        'scope': 'openid email profile'  # Scope defines the access required
    }
)



def generate_nonce():
    """Generate a random nonce for security."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))



@app.route('/google/login')
def google_login():
    """Redirect to Google OAuth login."""
    nonce = generate_nonce()  # Generate a nonce
    session['nonce'] = nonce   # Store nonce in session
    redirect_uri = url_for('google_authorize', _external=True)
    return google.authorize_redirect(redirect_uri, nonce=nonce)


@app.route('/google/authorize')
def google_authorize():
    """Callback route for Google OAuth."""
    token = google.authorize_access_token()
    nonce = session.get('nonce')  # Retrieve nonce from session
    user_info = google.parse_id_token(token, nonce=nonce)  # Pass the nonce here
    session['email'] = user_info.get('email')
    return redirect(url_for('google_choose'))


@app.route('/google/choose',methods=['GET','POST'])
def google_choose():
    if request.method=='POST':
        is_doctor = True if request.form.get('userType')== 'doctor' else False
        if is_doctor:
            if mongo.db.doctors_profile.find_one({'email':session.get('email')}):
                data = mongo.db.doctors_profile.find_one({'email':session.get('email')})
                return render_template('/dashboards/doctorprofile.html',data=data)
            else:
                return redirect(url_for('doctorProfileUpdate'))
        else:
            if mongo.db.patient_profile.find_one({'email':session.get('email')}):
                data = mongo.db.patient_profile.find_one({'email':session.get('email')})
                return render_template('/dashboards/patientprofile.html',data=data)
            else:
                return redirect(url_for('patientUpdateProfilePage'))
        
    return render_template('/login/oauth_login.html')



#MAIN PAGES

#HOME PAGE
@app.route('/')
def homePage():
    return render_template('/main/home.html')
    
#ABOUT PAGE
@app.route('/about')
def aboutPage():
    return render_template('/main/about.html')
    
#SERVICES PAGE
@app.route('/services')
def servicesPage():
    return render_template('/main/services.html')
    

#DONATE PAGE
@app.route('/donate')
def donatePage():
    return render_template('/main/donate.html')





#login Pages
#patientLoginPage

@app.route('/login', methods=['GET', 'POST'])
def loginPage():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        is_doctor = request.form.get('isDoctor')  
        user_collection = mongo.db.doctors_users if is_doctor else mongo.db.patient_users
        user = user_collection.find_one({'email': email})
        if user:
            hash_password = user['password']
            if bycrypt.check_password_hash(hash_password, password):
                session['email'] = str(user['email'])  
                session['username'] = str(user['username'])
                session['is_doctor'] = is_doctor
                session['object_id'] = str(user['_id'])
                return redirect(url_for('dashboardPage'))
            else:
                return render_template('/login/login.html', message="Invalid credentials")
        else:
            return render_template('/login/login.html', message="User not found")
    return render_template('/login/login.html')






##
##
#DASHBOARD PAGES
##  

@app.route('/dashboard')
def dashboardPage():
    if session.get('email') is None:
        return redirect(url_for('loginPage'))
    
    email = session.get('email')
    
    if session.get('is_doctor'):
        doctor_data = mongo.db.doctors_profile.find_one({'email': email})
        if doctor_data:
            return render_template('/dashboards/doctor/doctor-profile.html', doctor=doctor_data)
        else:
            return redirect(url_for('doctorProfileUpdate'))
    else:
        patient_data = mongo.db.patient_profile.find_one({'email': email})
        if patient_data:
            return render_template('/dashboards/patient/patient-profile.html', patient=patient_data)
        else:
            return redirect(url_for('patientProfileUpdate'))
    return render_template('/dashboards/profile.html')  




@app.route('/doctor/profile/update', methods=['GET', 'POST'])
def doctorProfileUpdate():
    form = DoctorProfileForm()
    email = session.get('email')
    
    if not email:
        flash("Unauthorized access. Please log in.", "danger")
        return redirect(url_for('loginPage'))
    
    doctor = mongo.db.doctors_profile.find_one({'email': email})
    
    if request.method == 'POST':
        if form.validate_on_submit():
            profile_data = {
                'name': form.name.data.upper(),
                'specialization': form.specialization.data.upper(),
                'experience': form.experience.data,
                'qualifications': form.qualifications.data.upper(),
                'contact_number': form.contact_number.data,
                'clinic_hospital': form.clinic_hospital.data.upper(),
                'address': form.address.data.upper(),
                'gender': form.gender.data.capitalize() , # To ensure proper capitalization
                'user_id': session.get('object_id'),
                'no_posts':0
            }
            
            try:
                if doctor:
                    # Update the doctor's profile if it already exists
                    mongo.db.doctors_profile.update_one({'email': email}, {'$set': profile_data})
                else:
                    # Insert the new profile if the doctor doesn't exist
                    profile_data['email'] = email
                    mongo.db.doctors_profile.insert_one(profile_data)
                
                flash("Profile updated successfully!", "success")
                return redirect(url_for('dashboardPage'))
            except Exception as e:
                flash(f"An error occurred: {e}", "danger")
        else:
            flash("Please correct the errors in the form.", "danger")
    
    # Populate form fields with existing data if available
    if doctor:
        form.name.data = doctor.get('name')
        form.specialization.data = doctor.get('specialization')
        form.experience.data = doctor.get('experience')
        form.qualifications.data = doctor.get('qualifications')
        form.contact_number.data = doctor.get('contact_number')
        form.clinic_hospital.data = doctor.get('clinic_hospital')
        form.address.data = doctor.get('address')
    
    return render_template('/dashboards/doctor/doctorprofileupdate.html', form=form, doctor=doctor)

@app.route('/patient/profile/update', methods=['GET', 'POST'])
def patientProfileUpdate():
    form = PatientProfileForm()
    email = session.get('email')
    if not email:
        flash("Unauthorized access. Please log in.", "danger")
        return redirect(url_for('loginPage'))
    
    patient = mongo.db.patient_profile.find_one({'email': email})
    
    if request.method == 'POST':
        if form.validate_on_submit():
            profile_data = {
                'name': form.name.data.upper(),
                'age': form.age.data,
                'gender': form.gender.data.upper(),
                'blood_group': form.blood_group.data.upper(),
                'contact_number': form.contact_number.data,
                'email': email,
                'address': form.address.data.upper(),
                'medical_history': form.medical_history.data.upper(),
                'user_id': session.get('object_id'),
                'no_posts':0
            }
            if  session['email'] != profile_data['email']:
                mongo.db.patient_user.update_one({'email': session['email']}, {'$set': {'email': email}})
            try:
                if patient:
                    # Update the patient's profile if it already exists
                    mongo.db.patient_profile.update_one({'email': email}, {'$set': profile_data})
                else:
                    # Insert a new profile if it doesn't exist
                    profile_data['email'] = email
                    mongo.db.patient_profile.insert_one(profile_data)
                
                flash("Profile updated successfully!", "success")
                return redirect(url_for('dashboardPage'))
            except Exception as e:
                flash(f"An error occurred: {e}", "danger")
    
    # Populate form fields with existing data if available
    if patient:
        form.name.data = patient.get('name')
        form.age.data = patient.get('age')
        form.gender.data = patient.get('gender')
        form.blood_group.data = patient.get('blood_group')
        form.contact_number.data = patient.get('contact_number')
        form.address.data = patient.get('address')
        form.medical_history.data = patient.get('medical_history')
    
    return render_template('/dashboards/patient/patientprofileupdate.html', form=form, patient=patient)


#Signup page
#doctorSignupPage
@app.route('/signup/doctor', methods=['GET', 'POST'])
def signupPage():
    form = SignupForm()
    if request.method== 'POST':
        if form.validate_on_submit():
            username = form.username.data
            email = form.email.data
            password = form.password.data
            isDoctor = form.isDoctor.data
            collection = mongo.db.doctors_users if isDoctor else mongo.db.patient_users
            
            if collection.find_one({'email':email}):
                return render_template('signup/signup.html', form=form,message="Email already exists")
            else:
                hash_password = bycrypt.generate_password_hash(password).decode('utf-8')
                collection.insert_one({'username':username,'email':email,'password':hash_password})
            return redirect(url_for('loginPage'))
        else:
            return render_template('signup/signup.html', form=form,message="Invalid data")
    return render_template('signup/signup.html', form=form)


@app.route('/dashboards/top-doctors.html')
def topDoctorsPage():
    return render_template('/dashboards/top-doctors.html')


@app.route('/dashboards/mycomments.html')
def mycomments():
    return render_template('/dashboards/doctor/mycomments.html')





@app.route("/post", methods=["GET", "POST"])
def postPage():
    form = ReportProblemForm()
    if request.method == "POST":
        if form.validate_on_submit():
            data = {
            "name": form.name.data,
            "email": form.email.data,
            "contact": form.contact.data,
            "title": form.title.data,
            "description": form.description.data,
            "patient_id": session.get("object_id"),
            }
            mongo.db.posts.insert_one(data)
            mongo.db.patient_profile.update_one({"email": session.get("email")},{"$inc": {"no_posts": 1}})
            flash("Your problem has been submitted successfully!", "success")
            return redirect(url_for("general"))
        else:
            flash("Please correct the errors in the form.", "danger")
    return render_template("dashboards/post/newPost.html", form=form)






@app.route("/general", methods=["GET", "POST"])
def general():
    per_page = 3  # Number of posts per page
    page = int(request.args.get("page", 1))  # Get the current page, default is 1
    skip = (page - 1) * per_page  # Calculate the number of documents to skip
    posts = list(mongo.db.posts.find().skip(skip).limit(per_page))
    total_posts = mongo.db.posts.count_documents({})  
    total_pages = -(-total_posts // per_page)  # Calculate total pages (ceiling division)

    return render_template(
        "dashboards/post/general.html",
        posts=posts,
        current_page=page,
        total_pages=total_pages
    )













@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('homePage'))










































if __name__=='__main__':
   app.run(debug=True,port=3961) 