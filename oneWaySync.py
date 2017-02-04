#!/usr/bin/env python

"""
One way sync. All the features of todoist-habitrpg; nothing newer or shinier.
"""

#Python library imports - this will be functionalities I want to shorten
from habitica import api #Note: you will want to get a version with API 3 support. At the time of this writing, check submitted pulls on the Github. 
from os import path # will let me call files from a specific path
import requests
import scriptabit
import pickle
import todoist
import main
import random
import json
from hab_task import HabTask
from todo_task import TodTask

#Here's where I'm putting my login stuff for Todoist.
tod_user = main.tod_login('auth.cfg')
tod_projects = tod_user.projects.all()
tod_inboxID = tod_projects[0].data['id']

#Telling the site where the config stuff for Habitica can go and get a list of habitica tasks...
auth, hbt = main.get_started('auth.cfg')  

#Getting all complete and incomplete habitica dailies and todos
hab_tasks, r1, r2 = main.get_all_habtasks(auth)

#Okay, now I need a list of todoist tasks. How do achieve that. 
tod_tasks = []
tod_items = tod_user.items
tod_tasklist = tod_items.all()
for i in range(0, len(tod_tasklist)):
    tod_tasks.append(TodTask(tod_tasklist[i].data))

"""
Okay, I want to write a little script that checks whether or not a task is there or not and, if not, ports it. 	
"""

pkl_file = open('oneWay_matchDict.pkl','rb')
try: 
    matchDict = pickle.load(pkl_file)
except:
    matchDict = {}

pkl_file.close()

#We'll want to just... pull all the unmatched completed tasks out of our lists of tasks. Yeah? 
tod_uniq, hab_uniq = main.get_uniqs(matchDict, tod_tasks, hab_tasks)

#Also, update lists of tasks with matchDict file...
main.update_tod_matchDict(tod_tasks, matchDict)
main.update_hab_matchDict(hab_tasks, matchDict)

#Check for matchDicts in existing habitica codes
for hab in hab_tasks:
    try:
        tid = int(hab.alias)
    except:
        continue
    matchDict[tid] = {}
    matchDict[tid]['hab'] = hab
    tod = TodTask(tod_items.get_by_id(tid).data)
    matchDict[tid]['tod'] = tod

tod_uniq, hab_uniq = main.get_uniqs(matchDict, tod_tasks, hab_tasks)

r = []
for tod_task in tod_uniq:
    tid = tod_task.id
    if tid not in matchDict.keys():
        for hab_task in hab_uniq:
            if tod_task.name == hab_task.name:
                print("match!")
                matchDict[tid] = {}
                matchDict[tid]['hab'] = hab_task
                matchDict[tid]['tod'] = tod_task
                r.append(main.add_hab_id(tid,hab_task))

tod_uniq, hab_uniq = main.get_uniqs(matchDict, tod_tasks, hab_tasks)

for tod in tod_uniq:
    #if "ev" in tod.date_string: #right, I'm gonna just put that on notice for the moment while I work on this
    tid = tod.id
    new_hab = main.make_hab_from_tod(tod)
    r = main.write_hab_task(hbt,new_hab)
    if r.ok == False:
        matchDict[tid] = {}
        matchDict[tid]['tod'] = tod
        new_hab = main.get_hab_fromID(tid)
        matchDict[tid]['hab'] = new_hab
    matchDict[tid] = {}
    matchDict[tid]['tod'] = tod
    matchDict[tid]['hab'] = new_hab

#Check that anything which has recently been completed gets updated in hab
for tid in matchDict:
    print(tid)
    if matchDict[tid]['tod'].complete == 0: 
        if matchDict[tid]['hab'].completed == False:
            print("Both undone")
        elif matchDict[tid]['hab'].completed == True:
            fix_tod = tod_user.items.get_by_id(tid)
            fix_tod.close()
        else: 
            print("ERROR: check HAB %s" % tid)
    elif matchDict[tid]['tod'].complete == 1:
        if matchDict[tid]['hab'].completed == False:
            fix_hab = matchDict[tid]['hab']
            main.complete_hab_todo(hbt, fix_hab)
        elif matchDict[tid]['hab'].completed == True:
            print("both done")
        else: 
            print("ERROR: check HAB %s" % tid)
    else:
        print("ERROR: check TOD %s" % tid)

pkl_out = open('habtod_matchDict.pkl','w')
pickle.dump(matchDict, pkl_out)
pkl_out.close()
tod_user.commit()