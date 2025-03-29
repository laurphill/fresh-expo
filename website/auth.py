#for user authentication

from flask import Blueprint

#blueprint - a bunch of roots/urls inside of it

auth = Blueprint('auth', __name__) 

@auth.route('/login') #set up url to login
def login():
    return "<p>Login</p>"

@auth.route('/logout')#set up url to logout
def logout():
    return "<p>logout</p>"

@auth.route('/sign-up')#set up url to sign up
def sign_up():
    return "<p>sign up</p>"