#entry point for app
from templates import * # for html templates
from flask import Flask, render_template, redirect, url_for, flash #for taking user to pages without having to manually switch 
from flask_sqlalchemy import SQLAlchemy #database
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user #making login functionality easier
from flask_wtf import FlaskForm #validate data at all times and increased security for user input
from wtforms import StringField, PasswordField, SubmitField, BooleanField #appropriate inputs for username, password, and after submitting said inputs
from wtforms.validators import InputRequired, Length #controlling properties of inputs
from flask_bcrypt import Bcrypt #secure passwords/information

#initialize app
app = Flask(__name__)
#For hashing passwords
bcrypt = Bcrypt(app)

# Initialize database/set a secret key
app.config['SECRET_KEY'] = '00123801989349857773048209842893048'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

#reload user id from database
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#reload the user object from the user ID stored in the session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Set up class for user information data storage table
class User(db.Model, UserMixin):
    # To specify the columns, we create class variables that belong to the Column class
    id = db.Column(db.Integer, primary_key=True)        # a unique id
    username = db.Column(db.String(20), nullable=False, unique = True) #username storage
    password = db.Column(db.String(80), nullable=False) #password storage

#create tables
with app.app_context(): 
    db.create_all()

#Taking information for username and password to set up new account
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max = 20)], render_kw={"place_holder":"Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max = 20)], render_kw={"place_holder":"password"})
    submit = SubmitField("Register")    

    def validate_username(self, username): #validates if there is no other user with the same username, raises validation error if so
        existing_username = User.query.filter_by(username = username.data).first()
        if existing_username:     
            flash("That username already exists, please enter a different one.")
        
#Logging in 
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max = 20)], render_kw={"place_holder":"Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max = 20)], render_kw={"place_holder":"password"})
    remember_me = BooleanField(render_kw={"place_holder":"Remember me"})
    submit = SubmitField("Login") 

@app.route('/')
def home():
    return render_template("home.html")

#login page
@app.route('/login', methods = ['GET', 'POST']) 
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first() #checks if user is in database
        if user: #if the user is in the database
            if bcrypt.check_password_hash(user.password, form.password.data): #and if the password matches the user
                login_user(user)
                return redirect(url_for('dashboard'))
        else:
            flash("Incorrect username or password, try again.")
            return redirect(url_for('login'))
    return render_template("login.html", form=form)


#logs user out if clicked
@app.route("/logout", methods = ["GET","POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

#password recovery
@app.route("/recover_pass", methods = ["GET", "POST"])
def recover_pass():
    return render_template("recover_pass.html")
    
#register page
@app.route("/register", methods=['GET','POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit(): #will hash password for secure registration then create new user with given username
        hashed_password = bcrypt.generate_password_hash(form.password.data) #create the hashed password using bcrypt
        new_user = User(username=form.username.data, password = hashed_password) #set up user in database format
        db.session.add(new_user) #add new user to database
        db.session.commit() #commit changes
        return redirect(url_for('login')) #take user to login after registration
    #html for registration page
    return render_template("register.html",form=form)

#dashboard route
@app.route("/dashboard", methods = ["GET", "POST"])
def dashboard():
    return render_template("dashboard.html")

app.route("/settings")
@login_required
def settings():
    pass

if __name__ == "__main__":
    
    app.run(debug = True) 

