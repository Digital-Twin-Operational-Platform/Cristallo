'''
`dtApp/dtCode/finiteelement.py`


:Author: 
    Matthew Bonney


This function takes a pre-generated python script for ABAQUS and add the 
parametric input given from the user via DTOP-Cristallo. The units are given
based on the design blueprints (in-s-slinch), but also displays the SI equivalent
on the HTML scripts. The function takes the pre-generated script and the user 
input and generates a new script in ABAQUS's python scripting language.

Once the new script is generated, ABAQUS is then called through the command 
prompt. This requires the host machine to have ABAQUS installed and callable
via the prompt 'abaqus cae'. Check the terminal to verify that ABAQUS was called
correctly and there are no errors.
'''
from flask import render_template, request
import os
from dtApp import app
from dtApp import date

    
@app.route('/FEA',methods=['GET','POST'])
def Nominal():
    """
    This function sets the default values for the FEA simulation to be run in ABAQUS.
    The units for these values are in Imperial-inches consistant units [slinch,in,s]
    As a reference, 1 slinch = 12 slugs (1 slinch is the mass accelerated by 1 lbf at 1 in/s^2 acceleration)
    The slinch is also called : slug-inch, blob, slugette, and snail
    """
    form={'freq':40,'job':'Frequency-Tests','Young':1.015e7,'Nu':0.33,'Dens':2.5265e-4,'fl_mesh':0.5,'lg_mesh':0.5,'mt_mesh':0.25,'ft_mesh':0.25}
    return render_template('fea.html',form=form,date=date)

@app.route('/FEA_sub',methods=['GET','POST'])
def Submit():
    """
    This function takes the user input via the POST method to generate the FEA simulation.
    To perform this simulation, this function generates a separate ``.py`` file to run in ABAQUS.
    This script is generated from a pre-made macro generated to create this system.
    The generated macro is generalized for the parameters requested from the user to create a new .py file.
    
    Once the python script is generated, ABAQUS is called to run the analysis.
    This requires ABAQUS to be installed on the local machine and is callable via the "abaqus cae" command prompt.
    The scratch folder is found in "dtApp/dtData/ABAQUS_Scratch".
    The main files to look for are the *.dat and *.odb files.
    These contain the results of the simulation.
    """
    # Gather Values
    req = request.form
    freq=req.get('freq')
    job=req.get('job')
    Young=req.get('E')
    Nu=req.get('Nu')
    Dens=req.get('rho')
    fl_mesh=req.get('fl_mesh')
    lg_mesh=req.get('lg_mesh')
    mt_mesh=req.get('mt_mesh')
    ft_mesh=req.get('ft_mesh')
    # Write Script
    path = os.path.join("dtApp","dtData","ABAQUS_Scratch","RunScript.py")
    try:
        f=open(path,'w')
    except:
        f=open(path,'x')
    f.write('jname = "'+str(job)+'"\n')
    f.write('Young = '+str(Young)+'\n')
    f.write('density = '+str(Dens)+'\n')
    f.write('Nu = '+str(Nu)+'\n')
    f.write('Freq_Max = '+str(freq)+'\n')
    f.write('fl_mesh = '+str(fl_mesh)+'\n')
    f.write('ft_mesh = '+str(ft_mesh)+'\n')
    f.write('lg_mesh = '+str(lg_mesh)+'\n')
    f.write('mt_mesh = '+str(mt_mesh)+'\n')
    f.close()
    # Add verbose
    f=open(path,'a')
    pathg = os.path.join("dtApp","dtData","FEAVerbose.txt")
    g=open(pathg,'r')
    f.write(g.read())
    g.close()
    f.close()
    
    # Run Abaqus
    dirname= os.path.join("dtApp","dtData","ABAQUS_Scratch")
    os.chdir(dirname)
    os.system('abaqus cae -mesa -noGUI RunScript.py')
    os.chdir('..')
    os.chdir('..')
    os.chdir('..')
    return render_template('fea_2.html',ID=job,date=date)