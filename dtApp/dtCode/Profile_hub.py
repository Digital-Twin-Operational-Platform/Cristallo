from flask import render_template, request, redirect, url_for
import numpy as np, os, csv
from dtApp import app
from dtApp import date

def read_profile(filename):
    # Read in CSV for model parameters
    A=[]
    try:
        with open(filename,'r', newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=';',skipinitialspace=True)
            for row in spamreader:
                A.append(row)
        m1,m2,m3=float(A[0][0]),float(A[0][1]),float(A[0][2])
        k1,k2,k3=float(A[1][0]),float(A[1][1]),float(A[1][2])
        c1,c2,c3=float(A[2][0]),float(A[2][1]),float(A[2][2])
    except:
        print("Error in loading CSV File")
        m1,m2,m3=5.0,5.0,5.0
        k1,k2,k3=4000.0,4000.0,4000.0
        c1,c2,c3=2.0,2.0,2.0 
    form={'m1':m1,'m2':m2,'m3':m3,'k1':k1,'k2':k2,'k3':k3,'c1':c1,'c2':c2,'c3':c3}
    return(form)

@app.route('/Profile_Hub',methods=['GET','POST'])
def Hub():
    return render_template("Hub.html",date=date)

@app.route('/Select',methods=['GET','POST'])
def Display():
    uploaded_files = request.files["file"]
    filename = uploaded_files.filename
    filename='dtApp/dtData/profiles/' + filename
    # Read in CSV for model parameters
    form=read_profile(filename)
    return render_template("Profile_disp.html", date=date,form=form)

@app.route('/Pro_cbc',methods=['GET','POST'])
def Pro_CBC():
    uploaded_files = request.files["file"]
    filename = uploaded_files.filename
    filename='dtApp/dtData/profiles/' + filename
    # Read in CSV for model parameters
    form=read_profile(filename)
    return render_template("Pro_CBC.html", date=date,form=form)  
