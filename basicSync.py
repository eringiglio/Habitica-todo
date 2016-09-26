#!/usr/bin/env python

"""
Fuck it, I need to just get something quick and dirty that will WORK. More features to come later.
"""

#Python library imports - this will be functionalities I want to shorten
from habitica import api #Note: you will want to get a version with API 3 support. At the time of this writing, check submitted pulls on the Github. 
from os import path # will let me call files from a specific path
import requests
import scriptabit
import pickle
import todoist
from hab_task import HabTask
from todo_task import TodTask

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
tod_projects = tod_user.projects.all()
tod_inboxID = tod_projects[0].data['id']

#Telling the site where the config stuff for Habitica can go and get a list of habitica tasks...
auth, hbt = main.get_started('auth.cfg')  

#Todoist tasks are, I think, classes. Let's make Habitica tasks classes, too.
url = 'https://habitica.com/api/v3/tasks/user/'
response = requests.get(url,headers=auth)
hab_raw = response.json()
hab_tasklist = hab_raw['data'] #FINALLY getting something I can work with... this will be a list of dicts I want to turn into a list of objects with class hab_tasks. Hrm. Weeeelll, if I make a class elsewhere....

#keeping records of all our tasks
tod_tasks = []
hab_tasks = [] 

#No habits right now, I'm afraid, in hab_tasks--Todoist gets upset. So we're going to make a list of dailies and todos instead...
for task in hab_tasklist: 
    item = HabTask(task)
    if item.category == 'reward':
        pass
    elif item.category == 'habit': 
        pass
    else:
        hab_tasks.append(item)

#Okay, now I need a list of todoist tasks. How do achieve that. 
tod_tasks = []
tod_items = tod_user.items
tod_tasklist = tod_items.all()
for i in range(0, len(tod_tasklist)):
    tod_tasks.append(TodTask(tod_tasklist[i].data))

#Okay, I want to write a little script that checks whether or not a task is there or not and, if not, ports it. 	
    #Ugh, I can't get bidict to work with these object classes, so we're going to basically pull a list of two paired dictionaries instead: a dict and its mirror image.
    #So the contents of this file should now be not a dictionary, but a list of two paired dictionaries which should be inverses of each other. 
pkl_file = open('habtod_matchDict.pkl','rb')
matchDict_list = pickle.load(pkl_file)
pkl_file.close()

#We'll want to just... pull all the unmatched tasks out of our lists of tasks. Yeah? 
hab_dup = []
hab_uniq = []
tod_dup = []
tod_uniq = []
hab_dup = matchDict.keys()
hab_uniq = list(set(hab_tasks) - set(hab_dup))
tod_dup = matchDict.values()
tod_uniq = list(set(tod_tasks) - set(tod_dup))

#check to pull out all the unmatched tasks we DON'T see in matchDict, our dictionary of paired habitica and todoist tasks
for tod_task in tod_uniq[:]:
    for hab_task in hab_uniq[:]:
        if tod_task.name == hab_task.name:
            matchDict[hab_task] = tod_task
            dictMatch[tod_task] = hab_task
            nameDict[hab_task.name] = tod_task.name

hab_dup = matchDict.keys()
hab_uniq = list(set(hab_tasks) - set(hab_dup))
tod_dup = matchDict.values()
tod_uniq = list(set(tod_tasks) - set(tod_dup))

#Now we've confirmed that we don't have any accidental duplicates and that previously sent tasks are all knocked out of the way, it's time to add copies of the individual tasks...
for i in tod_uniq:
    main.write_hab_todo(hbt,i.name)

#I'm just assuming that all these tasks can be dumped in the inbox. See above for todoist Inbox ID code, which is located under login
for task in hab_uniq:
    tod_user.items.add(task.name,tod_inboxID)

#I also want to make sure that any tasks which are checked off AND have paired tasks agree on completion.
#If one is checked complete, both should be...
for t in matchDict: #make sure neither of these are used elsewhere in code
    if matchDict[t].complete == 0 and t.completed == "False": 
        pass
    elif matchDict[t].complete == 1 and t.completed == "True":
        matchDict.pop(item, None)
    else: 
        main.complete_hab_todo(hbt,t)
		tid = matchDict[t].id
        tod = tod_items.get_by_id(tid)
        tod.complete()
        
#Wrapping it all up: saving matchDict, committing changes to todoist
pkl_out = open('habtod_matchDict.pkl','w')
pickle.dump(matchDict, pkl_out)
pkl_out.close()
tod_user.commit()