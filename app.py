from Imports import *
from User_DB import Events, Class, User, Messages, ClassMessage, get_user_by_id, get_user_by_username, add_user_to_class

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
    username = StringField(validators=[Length(min=4, max = 20), Optional()], render_kw={"place_holder":"Username"})
    email = EmailField(validators=[Length(min=4, max = 100), Optional()], render_kw={"place_holder":"email"})
    password = PasswordField(validators=[Length(min=4, max = 20), Optional()], render_kw={"place_holder":"password"})
    nickname = StringField('Nickname', validators=[Optional()],render_kw={"place_holder":"nickname"})
    bio = StringField('Bio',validators=[Optional()],render_kw={"place_holder":"Bio"})
    major = StringField('Major',validators=[Optional()],render_kw={"place_holder":"Major"})
    submit = SubmitField('Update')

@app.route('/api/messages/send', methods=['POST'])
@login_required
def send_message():
    data = request.json
    print("Received data:", data)  # Debug log

    receiver_id = data.get('receiver_id')
    content = data.get('content')

    if not receiver_id or not content:
        return jsonify({'error': 'Receiver ID and content are required.'}), 400

    receiver = User.query.get(receiver_id)
    if not receiver:
        return jsonify({'error': 'Receiver not found.'}), 404

    try:
        message = Messages(sender_id=current_user.id, receiver_id=receiver_id, content=content)
        db.session.add(message)
        db.session.commit()
        return jsonify({'message': 'Message sent successfully!'}), 201
    except Exception as e:
        print("Database error:", e)  # Debug log
        return jsonify({'error': 'Failed to save message to the database.'}), 500

@app.route('/api/messages/<int:receiver_id>', methods=['GET'])
@login_required
def get_messages(receiver_id):
    print("Fetching messages for receiver ID:", receiver_id)  # Debug log
    messages = Messages.query.filter(
        ((Messages.sender_id == current_user.id) & (Messages.receiver_id == receiver_id)) |
        ((Messages.sender_id == receiver_id) & (Messages.receiver_id == current_user.id))
    ).order_by(Messages.timestamp).all()

    messages_data = [
        {
            'id': message.id,
            'sender_id': message.sender_id,
            'receiver_id': message.receiver_id,
            'content': message.content,
            'sender_username': message.sender.username,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
        for message in messages
    ]

    print("Messages found:", messages_data)  # Debug log

    return jsonify(messages_data), 200

@app.route('/chat/<int:friend_id>', methods=['GET'])
@login_required
def chat(friend_id):
    friend = User.query.get(friend_id)
    if not friend:
        flash('Friend not found.', 'error')
        return redirect(url_for('dashboard'))

    return render_template('chats.html', friend=friend)

@app.route('/api/classes/<int:class_id>/add_member', methods=['POST'])
@login_required
def add_member_to_class(class_id):
    data = request.json
    user_id = data.get('user_id')

    class_ = Class.query.get(class_id)
    if not class_:
        return jsonify({'error': 'Class not found.'}), 404

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    if user in class_.members:
        return jsonify({'error': 'User is already a member of the class.'}), 400

    class_.members.append(user)
    db.session.commit()

    return jsonify({'message': 'User added to the class successfully!'}), 200

@app.route('/api/classes/<int:class_id>/send_message', methods=['POST'])
@login_required
def send_class_message(class_id):
    data = request.json
    content = data.get('content')

    if not content:
        return jsonify({'error': 'Message content is required.'}), 400

    class_ = Class.query.get(class_id)
    if not class_:
        return jsonify({'error': 'Class not found.'}), 404

    if current_user not in class_.members:
        return jsonify({'error': 'You are not a member of this class.'}), 403

    message = ClassMessage(class_id=class_id, sender_id=current_user.id, content=content)
    db.session.add(message)
    db.session.commit()
    print("Message sent:", message)  # Debug log

    return jsonify({'message': 'Message sent successfully!'}), 201

@app.route('/class_chat/<int:class_id>', methods=['GET'])
@login_required
def class_chat(class_id):
    class_ = Class.query.get(class_id)
    if not class_:
        flash('Class not found.', 'error')
        return redirect(url_for('dashboard'))

    if current_user not in class_.members:
        flash('You are not a member of this class.', 'error')
        return redirect(url_for('dashboard'))

    return render_template('class_chats.html', class_=class_)

@app.route('/api/classes/<int:class_id>/messages', methods=['GET'])
@login_required
def get_class_messages(class_id):
    class_ = Class.query.get(class_id)
    if not class_:
        return jsonify({'error': 'Class not found.'}), 404

    if current_user not in class_.members:
        return jsonify({'error': 'You are not a member of this class.'}), 403

    messages = ClassMessage.query.filter_by(class_id=class_id).order_by(ClassMessage.timestamp).all()
    messages_data = [
        {
            'id': message.id,
            'sender_id': message.sender_id,
            'sender_username': message.sender.username,
            'content': message.content,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
        for message in messages
    ]

    return jsonify(messages_data), 200

@app.route("/calendar", methods = ["GET", "POST"])
@login_required
def calendar():
   #Fetch all events from the database
    events = Events.query.filter_by(user_id=current_user.id).all()
    # Convert events to a format FullCalendar can understand
    events_data = [
        {
            'id': event.id,  # Include the event ID
            'title': event.title,
            'start': event.start.strftime('%Y-%m-%d'),  # Convert datetime to string
            'end' : event.end.strftime('%Y-%m-%d') if event.end else None,  # Convert datetime to string
        }
        for event in events
    ]
    return render_template('calendar.html', events=events_data)

#for creating events
@app.route('/api/events', methods=['POST'])
@login_required
def create_event():
    data = request.json
    try:
        # Convert the 'start' string to a datetime object
        start_datetime = datetime.strptime(data['start'], '%Y-%m-%d')
        end_datetime = datetime.fromisoformat(data['end']) if data.get('end') else None 
        new_event = Events(
            title=data['title'], 
            start=start_datetime, 
            end=end_datetime,
            user_id=current_user.id)
        db.session.add(new_event)
        db.session.commit()
        return jsonify({'message': 'Event added successfully!'}), 201
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400
        
#for deleting events
@app.route('/api/events/<int:event_id>', methods=['DELETE'])
@login_required
def delete_event(event_id):
    event = Events.query.filter_by(id=event_id, user_id=current_user.id).first()
    if event:
        db.session.delete(event)
        db.session.commit()
        return jsonify({'message': 'Event deleted successfully!'}), 200
    else:
        return jsonify({'error': 'Event not found.'}), 404
    
#for dragging events
@app.route('/api/events/<int:event_id>', methods=['PUT'])
@login_required
def update_event(event_id):
    data = request.json
    event = Events.query.filter_by(id=event_id, user_id=current_user.id).first()
    if event:
        try:
            # Update the event details
            event.title = data['title']
            event.start = datetime.fromisoformat(data['start'])  # Convert ISO string to datetime
            event.end = datetime.fromisoformat(data.get('end')) if data.get('end') else None 
            db.session.commit()
            return jsonify({'message': 'Event updated successfully!'}), 200
        
        except ValueError:
            return jsonify({'error': 'Invalid date format.'}), 400
    else:
        return jsonify({'error': 'Event not found.'}), 404
    
@app.route('/api/events/delete_all', methods=['DELETE'])
@login_required
def delete_all_events():
    # Query all events for the current user
    events = Events.query.filter_by(user_id=current_user.id).all()

    if events:
        # Delete all events
        for event in events:
            db.session.delete(event)
        db.session.commit()
        return jsonify({'message': 'All events deleted successfully!'}), 200
    else:
        return jsonify({'error': 'No events found to delete.'}), 404

@app.route('/upload_profile_picture', methods=['POST'])
@login_required
def upload_profile_picture():
    if 'profile_picture' not in request.files:
        flash('No file uploaded.', 'error')
        return redirect(url_for('profile', username=current_user.username))

    file = request.files['profile_picture']

    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('profile', username=current_user.username))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Update the user's profile picture in the database
        current_user.profile_picture = filename
        db.session.commit()

        flash('Profile picture updated successfully!', 'success')
        return redirect(url_for('profile', username=current_user.username))
    else:
        flash('Invalid file type. Please upload an image file.', 'error')
        return redirect(url_for('profile', username=current_user.username))
    

@app.route('/upload_photo/<int:photo_id>', methods=['POST'])
@login_required
def upload_photo(photo_id):
    if 'photo' not in request.files:
        flash('No file uploaded.', 'error')
        return redirect(url_for('profile', username=current_user.username))

    file = request.files['photo']

    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('profile', username=current_user.username))

    if file and allowed_file(file.filename):
        filename = secure_filename(f"{current_user.id}_photo{photo_id}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Update the user's photo in the database
        if photo_id == 1:
            current_user.photo1 = filename
        elif photo_id == 2:
            current_user.photo2 = filename
        elif photo_id == 3:
            current_user.photo3 = filename

        db.session.commit()
        flash('Photo updated successfully!', 'success')
        return redirect(url_for('profile', username=current_user.username))
    else:
        flash('Invalid file type. Please upload an image file.', 'error')
        return redirect(url_for('profile', username=current_user.username))
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
                flash("Incorrect password.")
                return render_template("login.html", form=form)
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
        is_teacher = form.is_teacher.data,
        major = "",
        ) #set up user in database format
    
        db.session.add(new_user) #add new user to database
        db.session.commit() #commit changes

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('login')) #take user to login after registration
    #html for registration page
    return render_template("register.html",form=form)

#dashboard route
@app.route("/dashboard", methods = ["GET", "POST"])
@login_required
def dashboard():
    return render_template("dashboard.html", username = current_user.username, friends=current_user.friends)

@app.route("/settings/<username>", methods=["GET", "POST"])
@login_required
def settings(username):
    form = SettingsForm(obj=current_user)  # Pre-fill the form with the current user's data

    if form.validate_on_submit():
        # Update only the fields that are provided
        if form.username.data and form.username.data != current_user.username:
            current_user.username = form.username.data

        if form.email.data and form.email.data != current_user.email:
            current_user.email = form.email.data

        if form.nickname.data and form.nickname.data != current_user.nickname:
            current_user.nickname = form.nickname.data

        if form.bio.data and form.bio.data != current_user.bio:
            current_user.bio = form.bio.data

        if form.major.data and form.major.data != current_user.major:
            current_user.major = form.major.data

        if form.password.data:  # Only update the password if a new one is provided
            hashed_password = bcrypt.generate_password_hash(form.password.data)
            current_user.password = hashed_password

        db.session.commit()
        flash("Settings updated successfully!", "success")
        return redirect(url_for("profile", username=current_user.username))

    return render_template("settings.html", form=form, user=current_user)

@app.route("/profile/<username>", methods=['GET', 'POST'])
@login_required
def profile(username):
    form = SettingsForm()
    user = get_user_by_username(db.session, username)

    if current_user.username == username:
        return render_template('profile.html', user = current_user, form=form)
    else:
        return "Not your account bud🍔🍔🦛"

        
@app.route("/other_profile/<username>", methods=['GET', 'POST'])
@login_required
def other_profile(username):
    user = get_user_by_username(db.session, username)
    form = SettingsForm()
    return render_template('other_profile.html', user = user, form=form)

@app.route('/start_chat', methods = ["GET", "POST"])
@login_required
def start_chat():
    url = request.url
    match = re.search(r'[?&]username=([^&#]+)', url)
    scanned_username = match.group(1) if match else None
    user = get_user_by_username(db.session, scanned_username)
    ######
    # Currently unused, but the beginnings of a chat method
    return render_template('chats.html')

@app.route('/chats', methods = ["GET", "POST"])
@login_required
def chats():
    return render_template('chats.html')

@app.route('/organizations', methods = ["GET", "POST"])
@login_required
def organizations():
    return render_template('organizations.html')

@app.route('/resources', methods = ["GET", "POST"])
@login_required
def resources():
    return render_template('resources.html')

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

@app.route('/resources/dining', methods = ['GET', 'POST'])
@login_required 
def dining():
    return render_template('dining.html')
#on campus housing routes

@app.route('/legacy-park')
@login_required
def legacy_park():
    return render_template('legacy-park.html')

@app.route('/university-park-phase1')
@login_required
def university_park_phase_one():
    return render_template('university-park-phase1.html')

@app.route('/university-park-phase2')
@login_required
def university_park_phase_two():
    return render_template('university-park-phase2.html')

@app.route('/park-place')
@login_required
def park_place():
    return render_template('park-place.html')

@app.route('/adams-hall')
@login_required
def adams_hall():
    return render_template('adams-hall.html')

@app.route('/aswell-hall')
@login_required
def aswell_hall():
    return render_template('aswell-hall.html')

@app.route('/dudley-hall')
@login_required
def dudley_hall():
    return render_template('dudley-hall.html')

@app.route('/cottingham-hall')
@login_required
def cottingham_hall():
    return render_template('cottingham-hall.html')

@app.route('/graham-hall')
@login_required
def graham_hall():
    return render_template('graham-hall.html')

@app.route('/mitchell-hall')
@login_required
def mitchell_hall():
    return render_template('mitchell-hall.html')

@app.route('/richardson-hall')
@login_required
def richardson_hall():
    return render_template('richardson-hall.html')

@app.route('/robinson-suite')
@login_required
def robinson_suite():
    return render_template('robinson-suite.html')

@app.route('/potts-suite')
@login_required
def potts_suite():
    return render_template('potts-suite.html')
# Connect with other users via QR code
@app.route("/connect")
@login_required
def connect():
    return render_template("connect.html")

# QR code scanner route
@app.route('/qrscanner')
@login_required
def scan():
    return render_template('qrscanner.html')

# Route to add user when qr code scanned
@app.route('/scanned')
@login_required
def scanned():
    print(request.url)
    scanned_user_id = request.args.get('userId', type=int)
    friend = get_user_by_id(db.session, scanned_user_id)
    class_name = request.args.get('class')  # None if not provided

    if not friend:
        flash(f"User ID {scanned_user_id} not found.")
        return redirect(url_for('scan'))
    
    if not scanned_user_id and not class_name:
        flash("Invalid QR code.")
        return redirect(url_for('scan'))
    
    if current_user.is_teacher:
        add_user_to_class(db.session, class_name, friend.id)
        db.session.commit()
        return render_template('qrscanner.html', selected_class=class_name)

    
    if not current_user.is_teacher and scanned_user_id is not None:
        if scanned_user_id == current_user.id:
            flash("You can't add yourself.")
            return redirect(url_for('scan'))    

        if friend in current_user.friends:
            flash(f"You are already connected with {friend.username}.")
            return redirect(url_for('scan'))
        else:
            current_user.friends.append(friend)
            friend.friends.append(current_user)
            flash(f"Success! You are now connected with {friend.username}.")
            db.session.commit()
            return redirect(url_for('scan'))

    db.session.commit()

@app.route('/create_class')
@login_required
def create_class():
    url = request.url
    form = SettingsForm()
    # Extract the class name from the URL (e.g., after %class%)
    class_match = re.search(r'[?&]class=([A-Za-z0-9_]+)', url)
    class_name = class_match.group(1) if class_match else None
    
    # First, check if the class exists in the Classes table
    class_exists = db.session.query(Class).filter(Class.name == class_name).first()
    if not class_exists:
        # If the class doesn't exist, create it
        new_class = Class(name=class_name)
        db.session.add(new_class)
        db.session.commit()
        db.session.refresh(new_class)

        flash(f"Success! You have created the class {class_name}.")
        add_user_to_class(db.session, class_name, current_user.id)
        return render_template('profile.html', user = current_user, form=form)
    else:
        add_user_to_class(db.session, class_name, current_user.id)
        return render_template('profile.html', user = current_user, form=form)
        

# Generates a qr code with the user's id info
@app.route('/generate')
@login_required
def generate(class_name=None):
    
    user_id = current_user.id
    
    qr = QRCode(
    version=1,
    error_correction=ERROR_CORRECT_L,
    box_size=10,
    border=4,
    )

    qr_data = f"/scanned?userId={user_id}"

    if current_user.is_teacher and class_name:
        qr_data = f"/scanned?userId={user_id}&class={class_name}"

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
@login_required
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