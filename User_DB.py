from Imports import *

Verbose = False

friends_table = db.Table(
     'friends',
     Column('user_id', db.Integer, db.ForeignKey('users.id')),
     Column('friend_id', db.Integer, db.ForeignKey('users.id'))
 )

# Association table for class members
class_members = db.Table(
    'class_members',
    Column('class_id', db.Integer, db.ForeignKey('classes.id')),
    Column('user_id', db.Integer, db.ForeignKey('users.id'))
)

class Messages(db.Model):
    __tablename__ = 'messages'

    id = Column(db.Integer, primary_key=True)
    sender_id = Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = Column(db.Text, nullable=False)
    timestamp = Column(db.DateTime, default=datetime.now())

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

class Class(db.Model):
    __tablename__ = 'classes'

    id = Column(Integer, primary_key=True, autoincrement=True)  # Auto-incrementing primary key
    name = Column(String(50), unique=True, nullable=False)  # Username field, must be unique
    
    # Relationship for user_classes
    users = db.relationship('User', secondary='user_classes', backref='classes')

    # Relationship for class_members
    members = db.relationship('User', secondary='class_members', backref='member_of_classes')

class ClassMessage(db.Model):
    __tablename__ = 'class_messages'

    id = Column(db.Integer, primary_key=True)
    class_id = Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    sender_id = Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = Column(db.Text, nullable=False)
    timestamp = Column(db.DateTime, default=datetime.now())

    class_ = db.relationship('Class', backref='messages')
    sender = db.relationship('User', backref='class_messages')

class Events(db.Model):
    __tablename__ = 'events'

    id = Column(db.Integer, primary_key=True)  # Primary key
    title = Column(db.String(100), nullable=False)  # Event title
    end = Column(db.DateTime, nullable=True)  # Event end date and time (optional)
    start = Column(db.DateTime, nullable=False)  # Event start date and time
    date = Column(db.Date, nullable=True)    
    user_id = Column(
        db.Integer,
        db.ForeignKey('users.id', name='fk_events_user_id'),  # Foreign key to the users table
        nullable=False  # Set to False to enforce NOT NULL constraint
    )
    @property
    def time(self):
        return self.start.time() 

    # Relationship to the User model
    user = db.relationship('User', backref='events')

    def __init__(self, title, start, end, user_id):
        self.title = title
        self.start = start
        self.end = end  
        self.user_id = user_id
        with app.app_context():
            db.create_all() 
    
    def __repr__(self):
        return f"<Event(id={self.id}, title={self.title}, start={self.start}, end={self.end} user_id={self.user_id})>"   # Prints event info
     
class UserClass(db.Model):
    __tablename__ = 'user_classes'

    user_id = Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    class_id = Column(db.Integer, db.ForeignKey('classes.id'), primary_key=True)

class User(db.Model, UserMixin):
    __tablename__ = 'users'  # Define the table name

    id = Column(Integer, primary_key=True, autoincrement=True)  # Auto-incrementing primary key
    username = Column(String(50), unique=True, nullable=False)  # Username field, must be unique
    email = Column(String(100), unique=True, nullable=False)  # Email field, must be unique
    password = Column(String(100), nullable=False)  # Password field
    bio = Column(String(100), nullable = True, server_default="About Me")
    nickname = Column(String(50), unique=False, nullable = True, server_default="nickname")  # Username field, must be unique
    is_teacher = Column(Boolean, unique=False, nullable = False)  # Username field, must be unique
    profile_picture = Column(db.String(100), nullable=True)  # Profile picture field
    friends = db.relationship(
     'User',
     secondary=friends_table,
     primaryjoin=id==friends_table.c.user_id,
     secondaryjoin=id==friends_table.c.friend_id,
     backref='added_by'
 )
    display_picture = Column(db.String(100), nullable=True)  # Display picture field
    major = Column(db.String(100), nullable=True)  # Major field
    photo1 = Column(db.String(150), nullable=True)
    photo2 = Column(db.String(150), nullable=True)
    photo3 = Column(db.String(150), nullable=True)


    def __init__(self, username, email, password, bio="About Me", nickname="nickname", is_teacher=False, major = major):
        self.username = username
        self.email = email
        self.password = password
        self.nickname = nickname
        self.bio = bio
        self.is_teacher = is_teacher
        self.major = major
    

        with app.app_context():
            db.create_all()

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email}, nickname = {self.nickname}, bio = {self.bio}, major = {self.major})>"    # Prints user info

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

    if Verbose:
        if user_exists:
            flash(f"User ID {user_id}: {user_exists}")
        if not user_exists:
            flash(f"User ID {user_id} does not exist.")
        
    return user_exists

# Function to get a user by username
def get_user_by_username(db_session, username: str):
    user_exists = db_session.query(User).filter(User.username == username).first()
    if Verbose:
        flash(f"User with username {username}: {user_exists}")
        if not user_exists:
            flash(f'No user "{username}" exists.')
    return user_exists

# Function to update user information
def update_user(db_session, user_id: int, new_username: str, new_email: str, new_password: str, new_nickname: str, new_bio:str):
    user = db.session.query(User).filter(User.id == user_id).first()
    user_former = user
    
    email_exists = db.session.query(User).filter((User.email == new_email)).first()
    if email_exists:
        # If a user with the same email exists, return error message
        flash(f"Error: Email address '{new_email}' already exists.")
        return None
    
    username_exists = db.session.query(User).filter((User.username == new_username)).first()
    if username_exists:
        # If a user with the same username exists, return error message
        flash(f"Error: Username '{new_username}' already exists.")
        return None
    
    if user:
        user.username = new_username
        user.email = new_email
        user.password = new_password
        user.nickname = new_nickname
        user.bio = new_bio
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
            
def add_user_to_class(db_session, class_name, user_id):
    # Only proceed if a class_name was given
    if not class_name:
        flash(f"Class name must be provided.")
        return None

    # First, check if the class exists in the Classes table
    class_exists = db_session.query(Class).filter(Class.name == class_name).first()
    
    user = get_user_by_id(db_session, user_id)
    # Now, check if the user exists in the Users table
    if not user:
        flash(f"User with ID '{user_id}' not found.")
        return None
    
    # Check if the user is already enrolled in the class
    if not class_exists:
        # If the class doesn't exist, create it
        new_class = Class(name=class_name)
        db_session.add(new_class)
        db_session.commit()
        db_session.refresh(new_class)
        class_exists = new_class
        
    if class_exists not in user.classes:
        user.classes.append(class_exists)
        class_exists.users.append(user)
        db_session.commit()
        if current_user.is_teacher and user.id == current_user.id:
            flash(f"Created course '{class_exists.name}' successfully!")
        else:
            flash(f"User '{user.username}' successfully added to '{class_exists.name}'!")
    else:
        if current_user.is_teacher and user.id == current_user.id:
            flash(f"Course '{class_exists.name}' already exists.")
        else:
            flash(f"User {user.username} is already enrolled in '{class_exists.name}'.")
    
        return user
