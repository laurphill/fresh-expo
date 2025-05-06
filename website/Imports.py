# All imports
from flask import Flask, Response, jsonify, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy #database
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user #making login functionality easier
from flask_wtf import FlaskForm #validate data at all times and increased security for user input
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField, EmailField, DateTimeField, TextAreaField#appropriate inputs for username, password, and after submitting said inputs
from wtforms.validators import InputRequired, Optional, Length, DataRequired #controlling properties of inputs
from flask_bcrypt import Bcrypt #secure passwords/information
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, PickleType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from DateTime import DateTime
from datetime import date, datetime
from flask_migrate import Migrate
from qrcode import *
from io import *
from base64 import *
import re 
import os
from werkzeug.utils import secure_filename #to save files to the server
import uuid as uuid
import json
from flask_cors import CORS
#to allow database to be accessed from other domains
import uuid as uuid

#initialize app
app = Flask(__name__)
CORS(app)

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.cache = {}
# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'static/uploads/profile_pictures'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Initialize database/set a secret key
app.config['SECRET_KEY'] = '00123801989349857773048209842893048'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)