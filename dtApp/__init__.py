from flask import Flask
from config import Config

#def create_app(Config):
# This creates the Flask app
app = Flask(__name__)
# This defines where the static folder is
# app._static_folder ='./dtapp/static'
app.config.from_object(Config)

import subprocess
proc_date = subprocess.Popen('git log -1 --format=%cd', shell=True, stdout=subprocess.PIPE, )
if len(proc_date.communicate()[0])==0:
    result = subprocess.run('git init', shell=True) # use 'run' here because sequential execution is needed
    result = subprocess.run('git add config.py', shell=True)
    result = subprocess.run('git commit -m "enable date commit"', shell=True) 
    proc_date = subprocess.Popen('git log -1 --format=%cd', shell=True, stdout=subprocess.PIPE, )

date1 = proc_date.communicate()[0]
date2 = date1.decode().split(' ')
date = date2[2]+' '+date2[1]+' '+date2[4] 

# This imports routes and defines the context
from dtApp import routes

# This enables the documentation 
#import os
#projectpath = os.getcwd()
#sympath = os.path.join(projectpath,'dtApp','static','doc','_build')
#if not(os.path.isdir(sympath)):
#    print('Creating symbolic link to render documentation.')
#    docpath = os.path.join(projectpath,'dtDoc','_build')
#    os.symlink(docpath,sympath)
    
    

    
