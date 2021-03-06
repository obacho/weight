# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 09:19:35 2017

@author: rbomblies
"""

from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, DateField, BooleanField
from wtforms.validators import DataRequired, Optional

class AddForm(FlaskForm):
    date = DateField('date', validators=[Optional()])
    weight = FloatField('weight')#, validators=[DataRequired()])
    comment = StringField('comment', validators=[Optional()], default='')

class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=True)

class EditForm(FlaskForm):
    weight = FloatField('weight', validators=[DataRequired()])

class PlotForm(FlaskForm):
    start_date = DateField('start_date', format='%Y-%m-%d', validators=[Optional()])
    end_date = DateField('end_date', format='%Y-%m-%d', validators=[Optional()])
