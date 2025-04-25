from Imports import *

#For hashing passwords
bcrypt = Bcrypt(app)

#reload user id from database
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

engine = create_engine("sqlite:///database.db", connect_args={"check_same_thread": False})  # SQLite needs this argument
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Setting to get print statements for debugging
Verbose = True

friends_table = db.Table(
     'friends',
     db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
     db.Column('friend_id', db.Integer, db.ForeignKey('users.id'))
 )

class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer,
                            db.ForeignKey('users.id'),
                            primary_key=True)
    following_id = db.Column(db.Integer,
                             db.ForeignKey('users.id'),
                             primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now())

class User(db.Model, UserMixin):
    __tablename__ = 'users'  # Define the table name

    id = Column(Integer, primary_key=True, autoincrement=True)  # Auto-incrementing primary key
    username = Column(String(50), unique=True, nullable=False)  # Username field, must be unique
    email = Column(String(100), unique=True, nullable=False)  # Email field, must be unique
    password = Column(String(100), nullable=False)  # Password field
    bio = Column(String(100), nullable = True, server_default="About Me")
    profile_pic = Column(String(), nullable=True) 
    nickname = Column(String(50), unique=False, nullable = True, server_default="nickname")  # Username field, must be unique
    friends = db.relationship(
     'User',
     secondary=friends_table,
     primaryjoin=id==friends_table.c.user_id,
     secondaryjoin=id==friends_table.c.friend_id,
     backref='added_by'
 )

    def __init__(self, username, email, password, bio, nickname, profile_pic):
        self.username = username
        self.email = email
        self.password = password
        self.nickname = nickname
        self.bio = bio
        self.profile_pic = profile_pic

        with app.app_context():
            db.create_all()

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email}, nickname = {self.nickname}, bio = {self.bio}), profile_pic = {self.profile_pic}>"    # Prints user info
# Create all tables in the database

with app.app_context():
    db.metadata.create_all(bind=engine)

# Function to add a new user
def create_user(db_session, username: str, email: str, password: str):

    email_exists = db_session.query(User).filter((User.email == email)).first()
    if email_exists:
        # If a user with the same email exists, return error message
        flash(f"Error: Email address '{email}' already exists.")
        # return None
    
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
def update_user(db_session, user_id: int, new_username: str, new_email: str, new_password: str, new_nickname: str, new_bio:str, new_profile_pic):
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
    
    if request.method == 'POST':
        user.username = new_username
        user.email = new_email
        user.password = new_password
        user.nickname = new_nickname
        user.profile_pic = new_profile_pic
        user.bio = new_bio
        db_session.commit()
        db_session.refresh(user)
        return redirect(url_for('settings/<username>'))

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
    email = EmailField(validators=[InputRequired(),Length(min=4, max = 20)], render_kw={"place_holder":"email"})
    submit = SubmitField("Register")    

#Logging in 
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max = 20)], render_kw={"place_holder":"Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max = 20)], render_kw={"place_holder":"password"})
    remember_me = BooleanField(render_kw={"place_holder":"Remember me"})
    submit = SubmitField("Login") 

class SettingsForm(FlaskForm):
    username = StringField(validators=[Length(min=4, max = 20)], render_kw={"place_holder":"Username"})
    email = EmailField(validators=[Length(min=4, max = 100)], render_kw={"place_holder":"email"})
    password = PasswordField(validators=[Length(min=4, max = 20)], render_kw={"place_holder":"password"})
    nickname = StringField('Nickname',render_kw={"place_holder":"nickname"})
    bio = StringField('Bio',render_kw={"place_holder":"Bio"})
    profile_pic = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')



@app.route('/')
def homepage():
    return render_template("homepage.html")

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
    return redirect(url_for('homepage'))
#password recovery
@app.route("/recover_pass", methods = ["GET", "POST"])
def recover_pass():
    return render_template("recover_pass.html")
#register page
@app.route("/register", methods=['GET','POST'])
def register():
    form = RegisterForm()
    existing_user = User.query.filter_by(username=form.username.data).first()
    existing_email = User.query.filter_by(email=form.email.data).first()

    if existing_user:
        flash("Username already exists.", "error")
        return render_template("register.html", form=form)
    if existing_email:
        flash("Email already registered.", "error")
        return render_template("register.html", form=form)

    if form.validate_on_submit(): #will hash password for secure registration then create new user with given username
        hashed_password = bcrypt.generate_password_hash(form.password.data) #create the hashed password using bcrypt
        new_user = User(username=form.username.data, email = form.email.data, password = hashed_password, nickname = form.username.data, bio = "", profile_pic='') #set up user in database format
        db.session.add(new_user) #add new user to database
        db.session.commit() #commit changes
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('login')) #take user to login after registration
    return render_template("register.html",form=form)

#dashboard route
@app.route("/dashboard", methods = ["GET", "POST"])
def dashboard():
    return render_template("dashboard.html", username = current_user.username)


@app.route("/settings/<username>", methods = ["GET", "POST"])
@login_required
def settings(username):
    form = SettingsForm()
    if current_user.username == username:
        if form.validate_on_submit():
            # f = form.profile_pic.data
            # filename = secure_filename(f.filename)
            # file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # f.save(file_path)
            user = User.query.first()
            if user:
                user.username = form.username.data
                user.email = form.email.data
                user.nickname = form.nickname.data
                user.bio = form.bio.data
                # user.profile_pic = file_path
                db.session.commit()
                return redirect(url_for('settings', username=username))
            
    return render_template('settings.html', user=current_user, form=form)

@app.route("/profile/<username>", methods=['GET', 'POST'])
@login_required
def profile(username):
    form = SettingsForm()
    # user = get_user_by_username(db.session, username)

    if current_user.username == username:
        return render_template('profile.html', user = current_user, form=form)
    else:
        return "User not found", 404

@app.route("/other_profile/<username>", methods=['GET', 'POST'])
def other_profile(username):
    user = get_user_by_username(db.session, username)
    form = SettingsForm()
    return render_template('other_profile.html', user = user, form=form)

@app.route("/friend_profile/<username>", methods=['GET', 'POST'])
def friend_profile(username):
    user = get_user_by_username(db.session, username)
    form = SettingsForm()
    return render_template('other_profile.html', user = user, form=form)


@app.route('/friends', methods = ["GET", "POST"])
@login_required
def friends():
    return render_template('friends.html', friends=current_user.friends)


@app.route('/chats', methods = ["GET", "POST"])
@login_required
def chats():
    return render_template('chats.html')

@app.route('/resources', methods = ["GET", "POST"])
@login_required
def resources():
    return render_template('resources.html')

@app.route('/resources/opportunities', methods = ['GET', 'POST'])
@login_required 
def opportunities():
    return render_template('opportunities.html')

@app.route('/resources/advising', methods = ['GET', 'POST'])
@login_required 
def advising():
    return render_template('advising.html')

@app.route('/resources/offcampus', methods = ['GET', 'POST'])
@login_required 
def offcampus():
    return render_template('offcampus.html')

@app.route('/resources/oncampus', methods = ['GET', 'POST'])
@login_required 
def oncampus():
    return render_template('oncampus.html')

@app.route('/resources/spots', methods = ['GET', 'POST'])
@login_required 
def spots():
    return render_template('spots.html')

@app.route('/resources/food', methods = ['GET', 'POST'])
@login_required 
def food():
    return render_template('food.html')

@app.route('/calendar', methods = ['GET', 'POST'])
@login_required 
def calendar():
    return render_template('calendar.html')
# Connect with other users via QR code
@app.route("/connect")
def connect():
    return render_template("connect.html")

# QR code scanner route
@app.route('/scan')
def scan():
    return render_template('scan.html')

# Route to add user when qr code scanned
@app.route('/scanned')
def scanned():
    url = request.url
    match = re.search(r'(\d+)(?!.*\d)', url)  # Last number match
    scanned_user_id = int(match.group(1)) if match else None

    if not scanned_user_id:
        flash("Invalid QR code.")
        return redirect(url_for('connect'))

    if scanned_user_id == current_user.id:
        flash("You can't add yourself.")
        return redirect(url_for('connect'))    
    
    print(current_user.friends)
    friend = User.query.get(scanned_user_id)

    if not friend:
        flash(f"User ID {scanned_user_id} not found.")
        return redirect(url_for('connect'))

    print(friend in current_user.friends)
    if friend in current_user.friends:
        flash(f"You are already connected with {friend.username}.")
        return redirect(url_for('connect'))

    current_user.friends.append(friend)
    print(friend)
    db.session.commit()
    print(current_user.friends)


    flash(f"Success! You are now connected with {friend.username}.")
    return redirect(url_for('dashboard'))

# Generates a qr code with the user's id info
@app.route('/generate')
def generate():
    user_id = current_user.id
    qr = QRCode(
    version=1,
    error_correction=ERROR_CORRECT_L,
    box_size=10,
    border=4,
    )
    qr_data = f"http://127.0.0.1:5000/scanned?userId={user_id}"  # Generates something like http://localhost:5000/connect?userId=4

    # Add data to the QR code
    qr.add_data(qr_data)
    
    # Generate QR code
    img = qr.make_image()

    # Convert image to base64 so we can embed it directly in HTML
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = b64encode(buffered.getvalue()).decode()

    return render_template("generate.html", qr_code_data=img_str)

if __name__ == "__main__":
    app.run(debug = True) 

