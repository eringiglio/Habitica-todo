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
import main

from subprocess import call # useful for running command line commands in python
from urllib2 import urlopen
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

"""
Okay, I want to write a little script that checks whether or not a task is there or not and, if not, ports it. 	
We're going to basically pull a list of two paired dictionaries instead: a dict and its mirror image.
So the contents of this file should now be not a dictionary, but a list of two paired dictionaries which should be inverses of each other. 
"""

pkl_file = open('habtod_matchDict.pkl','rb')
dict_list = pickle.load(pkl_file)
try: 
    matchDict = dict_list[0]
    dictMatch = dict_list[1]
except:
    matchDict = {}
    dictMatch = {}

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
for tod_task in tod_uniq:
    for hab_task in hab_uniq:
        if tod_task.name == hab_task.name:
            if hab_task in matchDict.keys():
                if tod_task in matchDict:
                    print("well done")
                else:
                    matchDict[hab_task] = tod_task
            else:
                matchDict[hab_task] = tod_task

#Ugh. I need to make sure I don't catch complete tasks in here. ugh. 
for task in tod_uniq:
    if task.complete == 1:
        tod_uniq.remove(task)

for task in hab_uniq:
    if task.completed == "True":
        hab_uniq.remove(task)

hab_dup = matchDict.keys()
hab_uniq = list(set(hab_tasks) - set(hab_dup))
tod_dup = matchDict.values()
tod_uniq = list(set(tod_tasks) - set(tod_dup))
    

#Now we've confirmed that we don't have any accidental duplicates and that previously sent tasks are all knocked out of the way, it's time to add copietos of the individual tasks...
for i in tod_uniq:
    hab = main.make_hab_from_tod(i)
    main.write_hab_task(hbt,hab)
'''    if ev in i.date_string:
        hab = main.make_daily_from_tod(i)
        main.write_hab_daily(hbt, hab)
    else:
        main.write_hab_todo(hbt,task)'''
    

#I'm just assuming that all these tasks can be dumped in the inbox. See above for todoist Inbox ID code, which is located under login
for task in hab_uniq:
    if task.category== "daily":
        tod_user.items.add(task.name,tod_inboxID,date_string=task.dailies_due)
    else:
        tod_user.items.add(task.name,tod_inboxID)

#I also want to make sure that any tasks which are checked off AND have paired tasks agree on completion.
#If one is checked complete, both should be...
for t in matchDict: #make sure neither of these are used elsewhere in code
    if matchDict[t].complete == 0: 
        if t.completed == False: 
            pass
        elif t.completed == True: 
            tid = matchDict[t].id
            tod = tod_items.get_by_id(tid)
            tod.complete()
        else:
            print("Hey, something's fishy here. Check out the Habitica task?")
            print(t.name)
    elif matchDict[t].complete == 1:
        if t.completed == True:
#            matchDict.pop(t, None)
#            dictMatch.pop(matchDict[t], None)
            pass
        elif t.completed == False: 
            main.complete_hab_todo(hbt,t)
        else:
            print("Hey, something's fishy here. Check out the Habitica task?")            
            print(t.name)
    else:
        print("uh, something's weird here. Check out the Todoist task?")
        print(matchDict[t].name)

#Wrapping it all up: saving matchDict, committing changes to todoist
dict_list = [matchDict, dictMatch]
pkl_out = open('habtod_matchDict.pkl','w')
pickle.dump(dict_list, pkl_out)
pkl_out.close()
tod_user.commit()