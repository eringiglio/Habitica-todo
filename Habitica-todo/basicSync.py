#!/usr/bin/env python

"""
Fuck it, I need to just get something quick and dirty that will WORK 
"""

#Python library imports - this will be functionalities I want to shorten
from habitica import api #Note: you will want to get a version with API 3 support. At the time of this writing, check submitted pulls on the Github. 
from pytodoist import todoist
from os import path # will let me call files from a specific path
import requests
import scriptabit

from subprocess import call # useful for running command line commands in python
from urllib2 import urlopen
import main 
from bisect import bisect
import json
import logging
import netrc
import sys 
from time import sleep
from webbrowser import open_new_tab
from docopt import docopt
from pprint import pprint


#Here's where I'm putting my login stuff for Todoist.

tod_names = []

#Telling the site where the config stuff for Habitica can go and get a list of habitica tasks...
auth, hbt = main.get_started('auth.cfg')  
hab_names =  main.get_hab_names(hbt)

#Todoist tasks are, I think, classes. Let's try an alternate way of getting the tasks I want....
url = 'https://habitica.com/api/v3/tasks/user/'
response = requests.get(url,headers=auth)
hab_raw = response.json()
hab_tasklist = hab_raw['data'] #FINALLY getting something I can work with... this will be a list of dicts I want to turn into a list of objects with class hab_tasks. Hrm. Weeeelll, if I make a class elsewhere....

#let's turn the hab task list into objects, not dictionaries....
hab_tasks = []

#One day I'm gonna find out how to do this on my own but this is not today, apparently
class Dict2Obj(object):
    """
    Turns a dictionary into a class
    """
    #----------------------------------------------------------------------
    def __init__(self, dictionary):
        """Constructor"""
        for key in dictionary:
            setattr(self, key, dictionary[key])

for task in hab_tasklist: 
    name = Dict2Obj(task)
    hab_tasks.append(name)

#Okay, now I need a list of todoist tasks. How do achieve that. 
tod_names = []
tod_tasks = tod_user.get_tasks()
for task in tod_tasks: 
    tod_names.append(task.content)

#Okay, I want to write a little script that checks whether or not a task is there or not and, if not, ports it. 	
habtod_match = "False"
	
for task in tod_tasks:
	for name in hab_tasks:
        if task.content == name.text:
            if task.checked == 0: 
                pass 
            else: 
                name.completed == "True"
	else:
		write_hab_todo(task.content)
			