from flask import Flask

def create_app(): #initialize application
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "df0iads0912931vasdfj0ivn03" #protects cookies for site
    
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix = '/') #slash means no prefix for going to blueprint
    app.register_blueprint(auth, url_prefix = '/')

    return app #return the app 