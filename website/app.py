#entry point for app
from templates import * # for html templates
from flask import Flask, render_template, redirect, url_for, flash #for taking user to pages without having to manually switch 
from flask_sqlalchemy import SQLAlchemy #database
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user #making login functionality easier
from flask_wtf import FlaskForm #validate data at all times and increased security for user input
from wtforms import StringField, PasswordField, SubmitField #appropriate inputs for username, password, and after submitting said inputs
from wtforms.validators import InputRequired, Length #controlling properties of inputs
from flask_bcrypt import Bcrypt #secure passwords/information
import jsonify

#initialize app
app = Flask(__name__)

#For hashing passwords
bcrypt = Bcrypt(app)

#reload user id from database
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#login existing users
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database/set a secret key
app.config['SECRET_KEY'] = '00123801989349857773048209842893048'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

#Set up class for user information data storage table
class User(db.Model, UserMixin):
    # To specify the columns, we create class variables that belong to the Column class
    id = db.Column(db.Integer, primary_key=True)        # a unique id
    username = db.Column(db.String(20), nullable=False, unique = True) #username storage
    password = db.Column(db.String(80), nullable=False) #password storage
   
    @classmethod
    def is_user_name_taken(cls, username):
      return db.session.query(db.exists().where(User.username==username)).scalar()

#create tables
with app.app_context(): 
    db.create_all()

#Taking information for username and password to set up new account
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max = 20)], render_kw={"place_holder":"Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max = 20)], render_kw={"place_holder":"password"})
    submit = SubmitField("Register")    

    def validate_username(self, username): #validates if there is no other user with the same username, raises validation error if so
        existing_user_username = User.query.filter_by(username = username.data).first()
        if existing_user_username:     
            duplicate_user()
        
#Logging in 
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max = 20)], render_kw={"place_holder":"Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max = 20)], render_kw={"place_holder":"password"})
    submit = SubmitField("Register")    

#home page
@app.route('/') 
def home():
    return render_template("home.html")

#login route
@app.route("/login", methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first() #checks if user is in database
        if user: #if the user is in the database
            if bcrypt.check_password_hash(user.password, form.password.data): #checks if pass and user match
                login_user(user) #then logs in user and redirects to dashbard
                return redirect(url_for("dashboard"))
        else:
            login_error() 
    return render_template("login.html", form=form)

#if an input is incorrect, flash message
def login_error():
    flash("Incorrect username or password, please try again")
    return redirect(url_for("login"))

#if a new user tries to register with a duplicate username, flash duplicate error message
def duplicate_user():
    flash("This username already exists, please try again")
    return redirect(url_for("register"))

#logout route
@app.route("/logout", methods = ["GET","POST"])
@login_required #user has to be logged in for this to work
def logout():
    logout_user() 
    return redirect(url_for("login"))

#register route
@app.route("/register", methods=['GET','POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit(): #will hash password for secure registration then create new user with given username
        hashed_password = bcrypt.generate_password_hash(form.password.data) #create the hashed password using bcrypt
        new_user = User(username=form.username.data, password = hashed_password) #set up user in database format
        db.session.add(new_user) #add new user to database
        db.session.commit() #commit changes
        return redirect(url_for('dashboard')) #take user to dashboard after registering
    #html for registration page
    return render_template("register.html",form=form)

#dashboard route
@app.route("/dashboard", methods = ["GET", "POST"])
def dashboard():
    #html for dashboard
    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(debug = True) 

