#!venv/bin/python
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 17 08:51:11 2017

@author: rbomblies
"""

from app import app
app.run(host= '0.0.0.0', port=6100, debug=True)
