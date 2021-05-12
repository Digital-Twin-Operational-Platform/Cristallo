'''
This function shows an interactive CAD model of the structure.
'''
from flask import render_template
from dtApp import app
from dtApp import date

@app.route('/cadmodel')
def cadmodel():
    return render_template('cadmodel.html',date=date)
