from flask import render_template, request, redirect, url_for, jsonify
from dtApp import app
import pandas as pd
import os
from dtLib.BillOfMaterials import part_connections
from dtLib import classes as cb
import subprocess
from subprocess import Popen, PIPE
from subprocess import check_output


@app.route("/knowg", methods=['GET', 'POST'])
def knowledge_graph():
    '''
    This route loads creates a knowledge graph from the Bill of Materials Exel file.

    Note that app.root_path is the absolute path to the root directory containing the app code.
    This should be ok for developement but may need changing to app.instance_path or os.path.dirname(app.instance_path) for implementation

    '''
    filename = os.path.join(app.root_path, 'static', 'BoM.xlsx')
    datafile = pd.ExcelFile(filename)
    n = cb.Entities()
    n.extractAllNodes(datafile)
    df1 = pd.DataFrame(n.componentnodes(), dtype="string")
    df2 = pd.DataFrame(n.assemblynodes(), dtype="string")
    # e = cb.Relations()
    # e.extractAllRelation(datafile)
    # g = cb.BuildGraph(n, e)
    # g.initialize()
    # start_neo4j()
    return render_template('knowg.html', tables=[df1.to_html(classes='data'), df2.to_html(classes='data')], titles=[df1.columns.values, df2.columns.values])


'''
Note that depedning on the os being used, you may need to include a function to start the neo4j server. Here is an approach using a shell script. Note this also may required neo4j and/or neo4j desktop to be installed, in which case you should start neo4j from the NEO4J_HOME directory
 
def start_neo4j():
    stdout = check_output([os.path.join(app.root_path, 'static', neo4j.sh']).decode('utf-8')
    return stdout

neo4j.sh
#!/bin/bash
echo ./neo4j start

'''
