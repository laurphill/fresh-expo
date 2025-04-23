from Imports import *
from User_DB import * 
from main import *

#Taking information for username and password to set up new account
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max = 20)], render_kw={"place_holder":"Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max = 20)], render_kw={"place_holder":"password"})
    email = EmailField(validators=[InputRequired(),Length(min=4, max = 20)], render_kw={"place_holder":"email"})
    submit = SubmitField("Register")    

#Logging in 
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max = 20)], render_kw={"place_holder":"Username"})
    email = EmailField(validators=[InputRequired(),Length(min=4, max = 20)], render_kw={"place_holder":"email"})
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
                return redirect(url_for('homepage'))
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
        new_user = User(username=form.username.data, email = form.email.data, password = hashed_password) #set up user in database format
        db.session.add(new_user) #add new user to database
        db.session.commit() #commit changes
        return redirect(url_for('login')) #take user to login after registration
    #html for registration page
    return render_template("register.html",form=form)

#dashboard route
@app.route("/home", methods = ["GET", "POST"])
def homepage():
    return render_template("homepage.html")

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
        return redirect(url_for('homepage'))

    try:
        scanned_user_id = int(scanned_user_id)
    except ValueError:
        flash("Invalid user ID format.")
        return redirect(url_for('homepage'))

    if scanned_user_id == current_user.id:
        flash("You can't add yourself.")
        return redirect(url_for('homepage'))

    db_session = SessionLocal()
    friend = get_user_by_id(db_session, scanned_user_id)

    if not friend:
        flash(f"User ID {scanned_user_id} not found.")
        return redirect(url_for('homepage'))

    if friend in current_user.friends:
        flash(f"You are already connected with {friend.username}.")
        return redirect(url_for('homepage'))

    current_user.friends.append(friend)
    db_session.commit()

    flash(f"Success! You are now connected with {friend.username}.")
    return redirect(url_for('connect'))

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

app.route("/settings")
@login_required
def settings():
    pass