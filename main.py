from Imports import *
from app import *
from User_DB import User

#reload user id from database
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

engine = create_engine("sqlite:///database.db", connect_args={"check_same_thread": False})  # SQLite needs this argument

# Create a sessionmaker instance to interact with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = SessionLocal()

#reload the user object from the user ID stored in the session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == "__main__":
    with app.app_context():
        #db.drop_all()
        #app.jinja_env.cache = {}
        db.create_all()
    app.run(debug=True)