#to store roots for website (pages)

from flask import Blueprint, render_template

#blueprint - a bunch of roots/urls inside of it

views = Blueprint('views', __name__) 

@views.route('/') #homepage place holder
def home():
    return("hi")

