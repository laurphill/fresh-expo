from Imports import *

#For hashing passwords
bcrypt = Bcrypt(app)

#reload user id from database
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Setting to get print statements for debugging
Verbose = True

class User(db.Model):
    __tablename__ = 'users'  # Define the table name

    id = Column(Integer, primary_key=True, autoincrement=True)  # Auto-incrementing primary key
    username = Column(String(50), unique=True, nullable=False)  # Username field, must be unique
    email = Column(String(100), unique=True, nullable=False)  # Email field, must be unique
    password = Column(String(100), nullable=False)  # Password field

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"    # Prints user info

engine = create_engine("sqlite:///database.db", connect_args={"check_same_thread": False})  # SQLite needs this argument

# Create all tables in the database

with app.app_context():
    db.metadata.create_all(bind=engine)

# Create a sessionmaker instance to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to add a new user
def create_user(db_session, username: str, email: str, password: str):

    email_exists = db_session.query(User).filter((User.email == email)).first()
    if email_exists:
        # If a user with the same email exists, return error message
        flash(f"Error: Email address '{email}' already exists.")
        return None
    
    username_exists = db_session.query(User).filter((User.username == username)).first()
    if username_exists:
        # If a user with the same username exists, return error message
        flash(f"Error: Username '{username}' already exists.")
        return None
    
    new_user = User(username=username, email=email, password=password)
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)
    flash(f"User Created: {new_user}")
    return new_user

# Function to get a user by ID
def get_user_by_id(db_session, user_id: int):
    
    user_exists = db_session.query(User).filter(User.id == user_id).first()

    if Verbose == True:
        if user_exists:
            flash(f"User ID {user_id}: {user_exists}")
        if not user_exists:
            flash(f"User ID {user_id} does not exist.")
        
    return user_exists

# Function to get a user by username
def get_user_by_username(db_session, username: str):
    user_exists = db_session.query(User).filter(User.username == username).first()
    if Verbose == True:
        flash(f"User with username {username}: {user_exists}")
        if not user_exists:
            flash(f'No user "{username}" exists.')
    return user_exists

# Function to update user information
def update_user(db_session, user_id: int, new_username: str, new_email: str, new_password: str):
    user = db_session.query(User).filter(User.id == user_id).first()
    user_former = user
    
    email_exists = db_session.query(User).filter((User.email == new_email)).first()
    if email_exists:
        # If a user with the same email exists, return error message
        flash(f"Error: Email address '{new_email}' already exists.")
        return None
    
    username_exists = db_session.query(User).filter((User.username == new_username)).first()
    if username_exists:
        # If a user with the same username exists, return error message
        flash(f"Error: Username '{new_username}' already exists.")
        return None
    
    if user:
        user.username = new_username
        user.email = new_email
        user.password = new_password
        db_session.commit()
        db_session.refresh(user)

    if Verbose:
        if user:
            flash(f"User {user_former} updated: {user}")
        if not user:
            flash(f"User ID {user_id} not found.")
    
    return user

# Function to delete a user
def delete_user(db_session, user_id: int):
    user = db_session.query(User).filter(User.id == user_id).first()
    
    if Verbose:
        if user:
            flash(f"Deleted user: {user}.")
        if not user:
            flash(f"No user with ID {user_id}.")
    
    if user:
        db_session.delete(user)
        db_session.commit()
        return user
    
    return None

#reload the user object from the user ID stored in the session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Taking information for username and password to set up new account
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max = 20)], render_kw={"place_holder":"Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max = 20)], render_kw={"place_holder":"password"})
    submit = SubmitField("Register")    

#Logging in 
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max = 20)], render_kw={"place_holder":"Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max = 20)], render_kw={"place_holder":"password"})
    remember_me = BooleanField(render_kw={"place_holder":"Remember me"})
    submit = SubmitField("Login") 

@app.route('/')
def landing():
    return render_template("landing.html")

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
@app.route("/home", methods = ["GET", "POST"])
def homepage():
    return render_template("homepage.html")

app.route("/settings")
@login_required
def settings():
    pass

if __name__ == "__main__":
    app.run(debug = True) 

