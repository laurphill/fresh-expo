# All imports
from flask import Flask, render_template, redirect, url_for, flash #for taking user to pages without having to manually switch 
from flask_sqlalchemy import SQLAlchemy #database
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user #making login functionality easier
from flask_wtf import FlaskForm #validate data at all times and increased security for user input
from wtforms import StringField, PasswordField, SubmitField, BooleanField #appropriate inputs for username, password, and after submitting said inputs
from wtforms.validators import InputRequired, Length #controlling properties of inputs
from flask_bcrypt import Bcrypt #secure passwords/information
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#initialize app
app = Flask(__name__)

# Initialize database/set a secret key
app.config['SECRET_KEY'] = '00123801989349857773048209842893048'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)