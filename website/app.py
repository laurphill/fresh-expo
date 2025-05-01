from Imports import *
from User_DB import *
from main import *

#Taking information for username and password to set up new account
class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max = 20)], render_kw={"place_holder":"Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max = 20)], render_kw={"place_holder":"password"})
    email = EmailField(validators=[InputRequired(),Length(min=4, max = 20)], render_kw={"place_holder":"email"})
    submit = SubmitField("Register")    
    is_teacher = BooleanField(render_kw={"place_holder":"is_teacher"})

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
    nickname = StringField('Nickname', validators=[DataRequired()],render_kw={"place_holder":"nickname"})
    bio = StringField('Bio',validators=[DataRequired()],render_kw={"place_holder":"Bio"})
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
        class_user = Class.query.filter_by(name=form.username.data).first() #checks if user is in database
        
        
        if user: #if the user is in the database
            if bcrypt.check_password_hash(user.password, form.password.data): #and if the password matches the user
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash("Incorrect password.")
                return render_template("login.html", form=form)
        elif class_user:
            login_user(class_user)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.")
            return render_template("login.html", form=form)
        
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

    if form.validate_on_submit(): #will hash password for secure registration then create new user with given username       
        # Check for existing username/email
        existing_user = User.query.filter_by(username=form.username.data).first()
        existing_email = User.query.filter_by(email=form.email.data).first()
        
        if existing_user:
            flash("Username already exists.", "error")
            return render_template("register.html", form=form)

        if existing_email:
            flash("Email already registered.", "error")
            return render_template("register.html", form=form)
        hashed_password = bcrypt.generate_password_hash(form.password.data) #create the hashed password using bcrypt
        
        # If user is a student/class, add to appropriate database

        new_user = User(
        username=form.username.data, 
        email = form.email.data, 
        password = hashed_password, 
        nickname = "", 
        bio = "",
        is_teacher = form.is_teacher.data
        ) #set up user in database format
    
        db.session.add(new_user) #add new user to database
        db.session.commit() #commit changes

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('login')) #take user to login after registration
    #html for registration page
    return render_template("register.html",form=form)

#dashboard route
@app.route("/dashboard", methods = ["GET", "POST"])
def dashboard():
    return render_template("dashboard.html", username = current_user.username, friends=current_user.friends)

#all routes that can only be accessed when user is logged in
@app.route("/settings")
@login_required
def settings_main():
    form = SettingsForm()
    return render_template('settings.html', form=form)

@app.route("/settings/<username>", methods = ["GET", "POST"])
@login_required
def settings(username):
    form = SettingsForm()
    if current_user.username == username:
        if form.validate_on_submit():
            user = User.query.first()
            if user:
                user.username = form.username.data
                user.email = form.email.data
                user.nickname = form.nickname.data
                user.bio = form.bio.data
                db.session.commit()
                return redirect(url_for('settings/<username>'))
        return render_template('settings.html', user=current_user, form=form)

@app.route("/profile/<username>", methods=['GET', 'POST'])
@login_required
def profile(username):
    form = SettingsForm()
    user = get_user_by_username(db.session, username)

    if current_user.username == username:
        return render_template('profile.html', user = current_user, form=form)
    elif user in current_user.friends:
        return render_template('friend_profile.html', user = user, form=form)
    elif user in db.session:
        return render_template('other_profile.html', user = user, form=form)
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


@app.route("/calendar", methods = ["GET", "POST"])
@login_required
def calendar():
    return render_template('calendar.html', events = events)

@app.route('/chats', methods = ["GET", "POST"])
@login_required
def chats():
    return render_template('chats.html')

@app.route('/friends', methods = ["GET", "POST"])
@login_required
def friends():
    return render_template('friends.html', friends=current_user.friends)


@app.route('/events', methods = ["GET", "POST"])
@login_required
def events():
    return render_template('events.html')

@app.route('/organizations', methods = ["GET", "POST"])
@login_required
def organizations():
    return render_template('organizations.html')

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

# Connect with other users via QR code
@app.route("/connect")
def connect():
    return render_template("connect.html")

# QR code scanner route
@app.route('/qrscanner')
def scan():
    return render_template('qrscanner.html')

# Route to add user when qr code scanned
@app.route('/scanned')
def scanned():
    url = request.url
    match = re.search(r'(\d+)(?!.*\d)', url)  # Last number match
    scanned_user_id = int(match.group(1)) if match else None
    
    # Extract the class name from the URL (e.g., after %class%)
    class_match = re.search(r'[?&]class=([A-Za-z0-9_]+)', url)
    class_name = class_match.group(1) if class_match else None
    
    if not scanned_user_id and not class_name:
        flash("Invalid QR code.")
        return redirect(url_for('connect'))
    
    if current_user.is_teacher:
        add_class_to_user(db_session, friend.id, class_name)
        friend.classes.append(current_user)
        flash(f"Success! You are now in {friend.username}'s class.")
        db.session.commit()
        return redirect(url_for('scan'))
    
    if scanned_user_id is not None:
        if scanned_user_id == current_user.id:
            flash("You can't add yourself.")
            return redirect(url_for('scan'))    
        
        friend = User.query.get(scanned_user_id)
        
        if not friend:
            flash(f"User ID {scanned_user_id} not found.")
            return redirect(url_for('scan'))

        if friend in current_user.friends:
            flash(f"You are already connected with {friend.username}.")
            return redirect(url_for('scan'))
        else:
            current_user.friends.append(friend)
            flash(f"Success! You are now connected with {friend.username}.")
            db.session.commit()
            return redirect(url_for('scan'))

    
    db.session.commit()

@app.route('/create_class')
def create_class():
    url = request.url

    # Extract the class name from the URL (e.g., after %class%)
    class_match = re.search(r'[?&]class=([A-Za-z0-9_]+)', url)
    class_name = class_match.group(1) if class_match else None
    
    # First, check if the class exists in the Classes table
    class_exists = db_session.query(Class).filter(Class.name == class_name).first()
    if not class_exists:
        # If the class doesn't exist, create it
        new_class = Class(name=class_name)
        db_session.add(new_class)
        db_session.commit()
        db_session.refresh(new_class)
        flash(f"Success! You have created the class {class_name}.")
        return redirect(url_for('profile'))
    else:
        flash(f"That class already exists.")

        
        

# Generates a qr code with the user's id info
@app.route('/generate')
def generate(class_name=None):
    user_id = current_user.id
    qr = QRCode(
    version=1,
    error_correction=ERROR_CORRECT_L,
    box_size=10,
    border=4,
    )

    qr_data = f"http://127.0.0.1:5000/scanned?userId={user_id}"  # Generates something like http://localhost:5000/connect?userId=4
    
    if current_user.is_teacher:
        qr_data = f"http://127.0.0.1:5000/scanned?%class_name=%{class_name}"  # Generates something like http://localhost:5000/connect?userId=4

    # Add data to the QR code
    qr.add_data(qr_data)
    
    # Generate QR code
    img = qr.make_image()

    # Convert image to base64 so we can embed it directly in HTML
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = b64encode(buffered.getvalue()).decode()

    return render_template("generate.html", qr_code_data=img_str)

@app.route('/join_class', methods=['POST'])
def join_class():
    # Get the user_id and class_id from the request body
    data = request.get_json()
    user_id = data.get('user_id')
    class_id = data.get('class_id')

    print(class_id)

    # Find the user and class
    user = User.query.get(user_id)
    class_ = Class.query.get(class_id)

    print(class_)

    if user and class_:
        # Check if the user is already in the class
        if class_ in user.class_list:
            return jsonify({'success': False, 'message': 'User is already in the class.'})

        # Add the user to the class
        user.class_list.append(class_)
        db.session.commit()

        return jsonify({'success': True, 'message': 'User successfully added to class.'})
    else:
        return jsonify({'success': False, 'message': 'User or Class not found.'})
