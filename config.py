# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 09:17:53 2017

@author: rbomblies
"""

import os
basedir = os.path.abspath(os.path.dirname(__file__))

APP_LOGGING_LEVEL = os.getenv('APP_LOGGING_LEVEL', default="ERROR")
DEBUG = APP_LOGGING_LEVEL == 'DEBUG'

WTF_CSRF_ENABLED = True
SECRET_KEY = 'adsfhafdfq74$ajdsfFFJFFi37!/$'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False

