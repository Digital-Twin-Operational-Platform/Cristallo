'''
This function updates the parameters of the 3dof model.
'''
from flask import render_template
from dtApp import app
from dtApp import date

@app.route('/lpm_update')
def lpm_update():
    return render_template('lpm_update.html',date=date)
