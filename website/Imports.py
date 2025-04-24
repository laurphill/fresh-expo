# All imports
from flask import Flask, render_template, redirect, url_for, flash, request #for taking user to pages without having to manually switch 
from flask_sqlalchemy import SQLAlchemy #database
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user #making login functionality easier
from flask_wtf import FlaskForm #validate data at all times and increased security for user input
from wtforms.validators import InputRequired, Length, DataRequired #controlling properties of inputs
from wtforms import StringField, PasswordField, SubmitField, BooleanField, EmailField, DateTimeField, TextAreaField#appropriate inputs for username, password, and after submitting said inputs
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from DateTime import DateTime
from datetime import date, datetime
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt #secure passwords/information
from qrcode import *
from io import *
from base64 import *
import re

#initialize app
app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.cache = {}

# Initialize database/set a secret key
app.config['SECRET_KEY'] = '00123801989349857773048209842893048'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)