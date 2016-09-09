#!/usr/bin/env python

"""
Fuck it, I need to just get something quick and dirty that will WORK. More features to come later.
"""

#Python library imports - this will be functionalities I want to shorten
from habitica import api #Note: you will want to get a version with API 3 support. At the time of this writing, check submitted pulls on the Github. 
#from pytodoist import todoist
from os import path # will let me call files from a specific path
import requests
import scriptabit
import pickle
 
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
tod_user = main.tod_login('auth.cfg')
tod_names = []

#Telling the site where the config stuff for Habitica can go and get a list of habitica tasks...
auth, hbt = main.get_started('auth.cfg')  
hab_names =  main.get_hab_names(hbt)

#Todoist tasks are, I think, classes. Let's make Habitica tasks classes, too.
url = 'https://habitica.com/api/v3/tasks/user/'
response = requests.get(url,headers=auth)
hab_raw = response.json()
hab_tasklist = hab_raw['data'] #FINALLY getting something I can work with... this will be a list of dicts I want to turn into a list of objects with class hab_tasks. Hrm. Weeeelll, if I make a class elsewhere....

#keeping records of all our tasks
tod_tasks = []
hab_tasks = [] 

#let's turn the hab task list into objects, not dictionaries....

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

#No habits right now, I'm afraid, in hab_tasks--Todoist gets upset. So we're going to make a list of dailies and todos instead...
for task in hab_tasklist: 
    name = Dict2Obj(task)
    if name.type == 'reward':
        pass
    elif name.type == 'habit': 
        pass
    else:
        hab_tasks.append(name)

#Okay, now I need a list of todoist tasks. How do achieve that. 
tod_tasks = tod_user.get_tasks()

#Okay, I want to write a little script that checks whether or not a task is there or not and, if not, ports it. 	
pkl_file = open('habtod_matchDict.pkl','rb')
matchDict = pickle.load(pkl_file)
pkl_file.close()

#We'll want to just... pull all the unmatched tasks out of our lists of tasks. Yeah? 
hab_dup = matchDict.keys()
hab_uniq = set(hab_tasks) - set(hab_dup)
tod_dup = 

#check to pull out all the unmatched tasks we DON'T see in matchDict, our dictionary of paired habitica and todoist tasks
for task in tod_tasks[:]:
    for name in hab_tasks[:]:
        if task.content == name.text:
            matchDict[name] = task
            tod_tasks.remove(task)
            hab_tasks.remove(name)
            
#Now we've confirmed that we don't have any accidental duplicates and that previously sent tasks are all knocked out of the way, it's time to add copies of the individual tasks...
for task in tod_tasks:
    main.write_hab_todo(hbt,task.content)

#I'm just assuming that all these tasks can be dumped in the inbox.
inbox = tod_user.get_project('Inbox')
for name in hab_tasks:
    inbox.add_task(name.text)

#I also want to make sure that any tasks which are checked off AND have paired tasks agree on completion.
#If one is checked complete, both should be...
for item in matchDict: #make sure neither of these are used elsewhere in code
    if task.checked == 0 and name.completed == "False": 
        pass
    elif task.checked == 1 and name.completed == "True":
        matchDict.pop(item, None)
    else: 
        name.completed = "True"
        task.checked = 1