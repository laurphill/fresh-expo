#to store roots for website (pages)

from flask import Blueprint, render_template

#blueprint - a bunch of roots/urls inside of it

views = Blueprint('views', __name__) 

@views.route('/') #empty slash for homepage
def home():
    return render_template("home.html")

#render html inside the home template