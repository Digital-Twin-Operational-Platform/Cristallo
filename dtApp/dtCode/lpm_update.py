'''
This function updates the parameters of the 3dof model.
'''
from flask import render_template
from dtApp import app
from dtApp import date
from numpy import genfromtxt


@app.route('/lpm_update', methods=['GET','POST'])
def lpm_update():
    frf_h11 = genfromtxt('dtData/test_1.csv', delimiter=',')
    
    return render_template('lpm_update.html',date=date)
