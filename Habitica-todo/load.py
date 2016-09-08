#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Here's all the gear needed to load up habitica's API...
May be nonfunctional with current code contained in main. 
"""
import main 
from os import path 
import requests

#Telling the site where the config stuff for Habitica can go......
file_path = path.expanduser('~/habitica/auth.cfg')
auth = open(file_path)

#And here's where my Habitica API keys are gonna go.
core.load_auth(auth)
