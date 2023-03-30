"""
routes.py
---------

The core script of the dtop project

Add to the list of import below your project module.
"""

from flask import render_template, request, redirect, url_for, flash, abort, session, jsonify, Blueprint

# Each route file needs to be imported separately
from .dtCode import cadmodel
from .dtCode import CBsimulator
from .dtCode import control 
from .dtCode import crossvalidation as CV
from .dtCode import design
from .dtCode import finiteelement
# from .dtCode import lpm_update
from .dtCode import nonlinearcbc as CBC
# from .dtCode import Profile_Compare
# from .dtCode import Profile_hub
from .dtCode import simulator
from .dtCode import unquant



bp = Blueprint('Cristallo', __name__)

from digitaltwin import date
@bp.route('/')
@bp.route('/home')
@bp.route('/index')
def home():
    return render_template("home.html",date=date)

@bp.route("/docs")
def docs():
    return render_template("docs.html",date=date)

@bp.app_errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404
# CAD Model
bp.add_url_rule('/cadmodel', view_func=cadmodel.cadmodel)
# Class Based Simulator
bp.add_url_rule('/CBsimulator',view_func=CBsimulator.CBsimula,methods=['GET','POST'])
# Control
bp.add_url_rule('/control',view_func=control.control,methods=['GET','POST'])
# Cross Validation
bp.add_url_rule('/crossval',view_func=CV.ExpValidation_Updated)
bp.add_url_rule('/crossval_1',view_func=CV.Exp_Data)
bp.add_url_rule('/crossval_2',view_func=CV.Exp_Num_Data)
bp.add_url_rule('/crossval_3',view_func=CV.Num_Data)
bp.add_url_rule('/crossval_4',view_func=CV.Exp_Exp_Data)
# Design Under Uncertainty
bp.add_url_rule('/Design_under_uncertainty',view_func=design.dplot4M,methods=['GET','POST'])
bp.add_url_rule('/Design_under_uncertainty_output',view_func=design.OutDis,methods=['GET','POST'])
bp.add_url_rule('/Design_under_uncertainty_fisher',view_func=design.start_method,methods=['GET','POST'])
bp.add_url_rule('/Design_under_uncertainty_sensitivity',view_func=design.testt,methods=['GET','POST'])
# FEA Model
bp.add_url_rule('/FEA', view_func =  finiteelement.Nominal)
bp.add_url_rule('/FEA_sub', view_func =  finiteelement.Submit,methods=['GET','POST'])
bp.add_url_rule('/script_save', view_func = finiteelement.write_abaqus,methods=['GET','POST'])
# Profile Generation

# Nonlinear Control Based Continuation
bp.add_url_rule('/nonlinearcbc',view_func=CBC.bristolcbc,methods=['GET','POST'])
bp.add_url_rule('/par_submit',view_func=CBC.par_submit,methods=['GET','POST'])
bp.add_url_rule('/download',view_func=CBC.downloadFile,methods=['GET','POST'])
bp.add_url_rule('/bristolcbc_update_fws',view_func=CBC.bristolcbc_update_fws,methods=['GET','POST'])
bp.add_url_rule('/bristolcbc_update_asw',view_func=CBC.bristolcbc_update_asw,methods=['GET','POST'])
bp.add_url_rule('/bristolcbc_update_cbc',view_func=CBC.bristolcbc_update_cbc,methods=['GET','POST'])

# Profile Comparison

# Profile Hub

# Solo Simulator
bp.add_url_rule('/simulator',view_func=simulator.simula,methods=['GET','POST'])
# Uncertainty Quantification
bp.add_url_rule('/unquant',view_func=unquant.unquant,methods=['GET','POST'])