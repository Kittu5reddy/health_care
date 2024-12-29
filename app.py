#imports
from flask import Flask,render_template,request,url_for,flash,redirect,session
from flask_session import Session
from flask_bcrypt import Bcrypt




#database
from flask_pymongo import PyMongo
from api_keys import mongodb

#Form imports
from forms import SignupForm,DoctorProfileForm



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
app.config['SECRET_KEY'] = 'your_secret_key_here'  
app.config['GOOGLE_CLIENT_ID'] = google_keys['client_id']
app.config['GOOGLE_CLIENT_SECRET'] = google_keys['client_secret']
app.config['GOOGLE_DISCOVERY_URL'] = 'https://accounts.google.com/.well-known/openid-configuration'


from datetime import timedelta



#session config
app.config['SESSION_TYPE'] = 'mongodb'
app.config['SESSION_PERMANENT'] = True 
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  
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


#CONTACT PAGE    
@app.route('/contact')
def contactPage():
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
##
# @app.route('/dashboard')
# def dashboardPage():
#     if session.get('email') is None:
#         return redirect(url_for('loginPage'))
#     if session.get('is_doctor'):
#         if mongo.db.doctors_profile.find_one({'email':session.get('email')}):
#             data = mongo.db.doctors_profile.find_one({'email':session.get('email')})
#             return render_template('/dashboards/doctor/doctor-profile.html',data=data)
#         else:
#             return redirect(url_for('doctorProfileUpdate'))
#     # else:
#     #     if mongo.db.patient_profile.find_one({'email':session.get('email')}):
#     #         data = mongo.db.patient_profile.find_one({'email':session.get('email')})
#     #         return render_template('/dashboards/doctor/patientprofile.html',data=data)
#     #     else:
#     #         return redirect(url_for('patientUpdateProfilePage'))
#     return render_template('/dashboards/profile.html')


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
            return render_template('/dashboards/patient/patientprofile.html', data=patient_data)
        else:
            return redirect(url_for('patientProfileUpdate'))
    return render_template('/dashboards/profile.html')  # Fallback for unexpected cases

@app.route('/doctor/profile/update', methods=['GET', 'POST'])
def doctorProfileUpdate():
    print(1)
    
    form = DoctorProfileForm()
    email = session.get('email')
    
    if not email:
        flash("Unauthorized access. Please log in.", "danger")
        return redirect(url_for('loginPage'))
    
    doctor = mongo.db.doctors_profile.find_one({'email': email})
    
    if request.method == 'POST':
        print(2)
        if form.validate_on_submit():
            print(3)
            profile_data = {
                'name': form.name.data.upper(),
                'specialization': form.specialization.data.upper(),
                'experience': form.experience.data,
                'qualifications': form.qualifications.data.upper(),
                'contact_number': form.contact_number.data,
                'clinic_hospital': form.clinic_hospital.data.upper(),
                'address': form.address.data.upper(),
                  # Handle image upload appropriately
            }
            print(profile_data)
            
            if doctor:
                mongo.db.doctors_profile.update_one({'email': email}, {'$set': profile_data})
            else:
                print('jiii')
                profile_data['email'] = email
                mongo.db.doctors_profile.insert_one(profile_data)
            
            flash("Profile updated successfully!", "success")
            return redirect(url_for('dashboardPage'))
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



































@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('homePage'))










































if __name__=='__main__':
   app.run(debug=True,port=3961) 