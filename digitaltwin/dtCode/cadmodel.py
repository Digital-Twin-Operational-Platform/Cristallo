'''
This function shows an interactive CAD model of the structure.
'''
from flask import render_template
# from . import digitaltwin

# @digitaltwin.bp.route('/cadmodel', methods=['GET','POST'])
def cadmodel():
    return render_template('cadmodel.html',date="date")
