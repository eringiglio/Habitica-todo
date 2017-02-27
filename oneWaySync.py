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
from datetime import datetime
from dateutil import parser

#Here's where I'm putting my login stuff for Todoist.
tod_user = main.tod_login('auth.cfg')
tod_user.sync()
tod_projects = tod_user.projects.all()
tod_inboxID = tod_projects[0].data['id']

#Telling the site where the config stuff for Habitica can go and get a list of habitica tasks...
auth = main.get_started('auth.cfg')  

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

#Also, update lists of tasks with matchDict file...
matchDict = main.update_tod_matchDict(tod_tasks, matchDict)
matchDict = main.update_hab_matchDict(hab_tasks, matchDict)

hab_uniq = []
#Check for matchDicts in existing habitica codes
for hab in hab_tasks:
    try:
        tid = int(hab.alias)
    except:
        hab_uniq.append(hab)
    matchDict[tid] = {}
    matchDict[tid]['hab'] = hab
    try:
        tod = TodTask(tod_items.get_by_id(tid).data)
        matchDict[tid]['tod'] = tod
        matchDict[tid]['recurs'] = tod.recurring
    except:
        matchDict.pop(tid)

#We'll want to just... pull all the unmatched completed tasks out of our lists of tasks. Yeah? 
tod_uniq, hab_uniq = main.get_uniqs(matchDict, tod_tasks, hab_tasks)

#Okay, so what if there are two matched tasks in the two uniq lists that really should be paired?
for tod_task in tod_uniq:
    tid = tod_task.id
    if tid not in matchDict.keys():
        for hab_task in hab_uniq:
            if tod_task.name == hab_task.name:
                r = main.add_hab_id(tid,hab_task)
                if r.ok == False:
                    print("Error updating hab %s! %s" % (hab.name,r.reason))
                else:
                    matchDict[tid] = {}
                    matchDict[tid]['hab'] = hab_task
                    matchDict[tid]['tod'] = tod_task


tod_uniq, hab_uniq = main.get_uniqs(matchDict, tod_tasks, hab_tasks)

#Here anything new in tod gets added to hab
for tod in tod_uniq:
    tid = tod.id
    if tod.recurring == "Yes":
        new_hab = main.make_daily_from_tod(tod)
    else:
        new_hab = main.make_hab_from_tod(tod)
    newDict = new_hab.task_dict
    r = main.write_hab_task(newDict)
    print("Added hab to %s!" % tod.name)
    print(r)
    if r.ok == False:
        matchDict[tid] = {}
        matchDict[tid]['tod'] = tod
        new_hab = main.get_hab_fromID(tid)
        matchDict[tid]['hab'] = new_hab
    matchDict[tid] = {}
    matchDict[tid]['tod'] = tod
    matchDict[tid]['hab'] = new_hab

r = []
#Check that anything which has recently been completed gets updated in hab
for tid in matchDict:
    tod = matchDict[tid]['tod']
    hab = matchDict[tid]['hab']
    if tod.recurring == 'Yes':
        if hab.dueToday == True:
            if hab.completed == False:
                if tod.dueToday == 'Yes':
                    matched_hab = main.sync_hab2todo(hab, tod)
                    r = main.update_hab(matched_hab)
                elif tod.dueToday == 'No':
                    r = main.complete_hab(hab)
                    print(hab.name)
                    print(r)
                    print('fix it! complete the damn hab!')
                else:
                    print("error in daily Hab")
            elif hab.completed == True:
                if tod.dueToday == 'Yes':
                    fix_tod = tod_user.items.get_by_id(tid)
                    fix_tod.close()
                    print('fix the tod! TID %s, NAMED %s' %(tid, tod.name))
                elif tod.dueToday == 'No':
                    continue
                else:
                    print("error, check todoist daily")
        elif hab.dueToday == False:
            continue
        else:
            print("error, check hab daily")
    elif tod.recurring == 'No':
        if tod.complete == 0: 
            if hab.completed == False:
                matched_hab = main.sync_hab2todo(hab, tod)
                r = main.update_hab(matched_hab)
            elif hab.completed == True:
                fix_tod = tod_user.items.get_by_id(tid)
                fix_tod.close()
                print('completed tod %s' % tod.name)
            else: 
                print("ERROR: check HAB %s" % tid)
                matchDict.pop(tid)
        elif tod.complete == 1:
            if hab.completed == False:
                r = main.complete_hab(hab)
                print(r)
                if r.ok == True:
                    print('Completed hab %s' % hab.name)
                else:
                    print('check hab ID %s' %tid)
                    print(r.reason)
            elif hab.completed == True:
                continue
            else: 
                print("ERROR: check HAB %s" % tid)
        else:
            print("ERROR: check TOD %s" % tid)
    
    r = []
    try: 
        dueNow =  str(parser.parse(matchDict[tid]['tod'].due_date).date())
    except:
        continue
    if dueNow != matchDict[tid]['hab'].date and matchDict[tid]['hab'].category == 'todo':
        matchDict[tid]['hab'].task_dict['date'] = dueNow
        r = main.update_hab(matchDict[tid]['hab']) 

pkl_out = open('oneWay_matchDict.pkl','w')
pickle.dump(matchDict, pkl_out)
pkl_out.close()
tod_user.commit()