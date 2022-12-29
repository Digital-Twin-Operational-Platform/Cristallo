"""
routes.py
---------

The core script of the dtop project

Add to the list of import below your project module.
"""

from flask import render_template, request, redirect, Response, url_for, send_file
from dtApp import app
from dtApp import date
import os
from config import Config

app.config.from_object(Config)
PROFILE_FOLDER = os.path.join('dtData','profiles')
app.config['PROFILE_FOLDER']= PROFILE_FOLDER

# Each route file needs to be imported separately
from .dtCode import unquant
from .dtCode import finiteelement
from .dtCode import control 
from .dtCode import crossvalidation # from .dtCode import ExpValidation_Updated
from .dtCode import cadmodel
from .dtCode import lpm_update
from .dtCode import Profile_hub
from .dtCode import Profile_Compare
from .dtCode import CBsimulator

@app.route('/')
@app.route('/home')
@app.route('/index')
def home():
    return render_template("home.html",date=date)

@app.route("/docs")
def docs():
    return render_template("docs.html",date=date)

@app.route("/contrib")
def contrib():
    return render_template("contrib.html",date=date)

if __name__ == '__main__':
	app.run(debug=True)
