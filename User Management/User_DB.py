from Imports import *

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
db.metadata.create_all(bind=engine)

# Create a sessionmaker instance to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Function to add a new user
def create_user(db_session, username: str, email: str, password: str):

    email_exists = db_session.query(User).filter((User.email == email)).first()
    if email_exists:
        # If a user with the same email exists, return error message
        print(f"Error: Email address '{email}' already exists.")
        return None
    
    username_exists = db_session.query(User).filter((User.username == username)).first()
    if username_exists:
        # If a user with the same username exists, return error message
        print(f"Error: Username '{username}' already exists.")
        return None
    
    new_user = User(username=username, email=email, password=password)
    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)
    print(f"User Created: {new_user}")
    return new_user

# Function to get a user by ID
def get_user_by_id(db_session, user_id: int):
    
    user_exists = db_session.query(User).filter(User.id == user_id).first()

    if Verbose == True:
        if user_exists:
            print(f"User ID {user_id}: {user_exists}")
        if not user_exists:
            print(f"User ID {user_id} does not exist.")
        
    return user_exists

# Function to get a user by username
def get_user_by_username(db_session, username: str):
    user_exists = db_session.query(User).filter(User.username == username).first()
    if Verbose == True:
        print(f"User with username {username}: {user_exists}")
        if not user_exists:
            print(f'No user "{username}" exists.')
    return user_exists

# Function to update user information
def update_user(db_session, user_id: int, new_username: str, new_email: str, new_password: str):
    user = db_session.query(User).filter(User.id == user_id).first()
    user_former = user
    
    email_exists = db_session.query(User).filter((User.email == new_email)).first()
    if email_exists:
        # If a user with the same email exists, return error message
        print(f"Error: Email address '{new_email}' already exists.")
        return None
    
    username_exists = db_session.query(User).filter((User.username == new_username)).first()
    if username_exists:
        # If a user with the same username exists, return error message
        print(f"Error: Username '{new_username}' already exists.")
        return None
    
    if user:
        user.username = new_username
        user.email = new_email
        user.password = new_password
        db_session.commit()
        db_session.refresh(user)

    if Verbose:
        if user:
            print(f"User {user_former} updated: {user}")
        if not user:
            print(f"User ID {user_id} not found.")
    
    return user

# Function to delete a user
def delete_user(db_session, user_id: int):
    user = db_session.query(User).filter(User.id == user_id).first()
    
    if Verbose:
        if user:
            print(f"Deleted user: {user}.")
        if not user:
            print(f"No user with ID {user_id}.")
    
    if user:
        db_session.delete(user)
        db_session.commit()
        return user
    
    return None

# Test the database by running this file directly
if __name__ == "__main__":
    # Create a session
    session = SessionLocal()

    # Add a new user to the database
    create_user(session, "john_doe", "john@example.com", "securepassword123")

    # Get user by ID
    get_user_by_id(session, 1)

    # Get user by username
    get_user_by_username(session, "john_doe")

    # Update user information
    update_user(session, 1, "john_updated", "john_updated@example.com", "newpassword456")

    # Add another new user to the database
    create_user(session, "jane_doe", "jane@example.com", "securepassword123")
    create_user(session, "jane_die", "jane_die@example.com", "securepassword123")
    # Get user by ID
    get_user_by_id(session, 1)  # John
    get_user_by_id(session, 2)  # Jane
    get_user_by_id(session, 3)  # Jane2
    
    



    ## Error messages ##
    new_user = create_user(session, "john_doe", "john@example.com", "securepassword123")

    # Update user information
    update_user(session, 1, "john_updated", "john@example.com", "newpassword456")
    update_user(session, 2, "john_updated", "Jane@example.com", "newpassword456")

    # Delete user
    delete_user(session, 1)
    session.commit()
    delete_user(session, 1)

    # Close the session
    session.close()

    # Session can be reopened with the data still present
    session = SessionLocal()

    get_user_by_id(session, 1)
    get_user_by_id(session, 2)

    session.query(User).delete()
    session.commit()
    get_user_by_id(session, 2)