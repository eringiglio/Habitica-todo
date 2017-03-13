#!/usr/bin/env python

"""
Main.py overdue for an overhaul! Let's see.
"""

"""Here's where we import stuff we need..."""
import todoist
import requests
import json
from hab_task import HabTask
from todo_task import TodTask
import os
import logging
try:
    import ConfigParser as configparser
except:
    import configparser	
from datetime import datetime
from dateutil import parser
import re


"""
Version control, basic paths
"""

VERSION = 'Habitica-todo version 2.0.0'
TASK_VALUE_BASE = 0.9747  # http://habitica.wikia.com/wiki/Task_Value
HABITICA_REQUEST_WAIT_TIME = 0.5  # time to pause between concurrent requests
HABITICA_TASKS_PAGE = '/#/tasks'
# https://trello.com/c/4C8w1z5h/17-task-difficulty-settings-v2-priority-multiplier
PRIORITY = {'easy': 1,
            'medium': 1.5,
            'hard': 2}
AUTH_CONF = os.path.expanduser('~') + '/.config/habitica/auth.cfg'
CACHE_CONF = os.path.expanduser('~') + '/.config/habitica/cache.cfg'

SECTION_CACHE_QUEST = 'Quest'

"""
Small utilities written by me start here.
"""

def get_all_habtasks(auth):
    #Todoist tasks are, I think, classes. Let's make Habitica tasks classes, too.
    url = 'https://habitica.com/api/v3/tasks/user/'
    response = requests.get(url,headers=auth)
    hab_raw = response.json()
    hab_tasklist = hab_raw['data'] #FINALLY getting something I can work with... this will be a list of dicts I want to turn into a list of objects with class hab_tasks. Hrm. Weeeelll, if I make a class elsewhere....
    
    #In order to get any records of completed tasks, I need to make a separate request...
    completedAuth = auth.copy()
    completedAuth['type'] = 'completedTodos'
    response2 = requests.get(url,headers=completedAuth)
    completed_raw = response2.json()['data']
    for i in completed_raw:
        hab_tasklist.append(i)
    
    #keeping records of all our tasks
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
    return(hab_tasks, response, response2)
    
def tod_login(configfile):
    logging.debug('Loading todoist auth data from %s' % configfile)

    try:
        cf = open(configfile)
    except IOError:
        logging.error("Unable to find '%s'." % configfile)
        exit(1)

    config = configparser.SafeConfigParser()
    config.readfp(cf)

    cf.close()

    # Get data from config
    try:
        rv = config.get('Todoist', 'api-token')

    except configparser.NoSectionError:
        logging.error("No 'Todoist' section in '%s'" % configfile)
        exit(1)

    except configparser.NoOptionError as e:
        logging.error("Missing option in auth file '%s': %s" % (configfile, e.message))
        exit(1)
    
    tod_user = todoist.TodoistAPI(rv)
    #tod_user = todoist.login_with_api_token(rv)
    # Return auth data
    return tod_user

def make_daily_from_tod(tod):
    import re
    new_hab = {'type':'daily'}
    new_hab['text'] = tod.name
    new_hab['alias'] = tod.id
    reg = re.compile(r"ev.{0,}(?<!other)\b (mon[^t]|tues|wed|thurs|fri|sun|sat|w(or|ee)kday|weekend)", re.I)
    
    match = reg.match(tod.date_string)
    if match:
        new_hab['frequency'] = 'weekly'
        daysofWeek = {}
        if 'sun' in tod.date_string:
            daysofWeek['su']  = True
        else:
            daysofWeek['su'] = False
        if 'mon' in tod.date_string:
            daysofWeek['m']  = True
        else:
            daysofWeek['m'] = False
        if 'tues' in tod.date_string:
            daysofWeek['t']  = True
        else:
            daysofWeek['t'] = False
        if 'wed' in tod.date_string:
            daysofWeek['w']  = True
        else:
            daysofWeek['w'] = False
        if 'thurs' in tod.date_string:
            daysofWeek['th']  = True
        else:
            daysofWeek['th'] = False
        if 'fri' in tod.date_string:
            daysofWeek['f']  = True
        else:
            daysofWeek['f'] = False
        if 'sat' in tod.date_string:
            daysofWeek['s']  = True
        else:
            daysofWeek['s'] = False
        if 'weekday' in tod.date_string:
            daysofWeek['m']  = True
            daysofWeek['t'] = True
            daysofWeek['w'] = True
            daysofWeek['th'] = True
            daysofWeek['f'] = True
        if 'weekend' in tod.date_string:
            daysofWeek['su'] = True
            daysofWeek['s'] = True
        new_hab['repeat'] = daysofWeek
    else:
        new_hab['frequency'] = 'daily'
        todStart = str(parser.parse(tod.due_date).date())
        new_hab['startDate'] = todStart
        new_hab['everyX'] = 1 
   
    if tod.priority == 1:
        new_hab['priority'] = 2
    elif tod.priority == 2:
        new_hab['priority'] = 1.5
    elif tod.priority == 3:
        new_hab['priority'] = 1
    elif tod.priority == 4:
        new_hab['priority'] = 1
        
    finished_hab = HabTask(new_hab)
    return finished_hab

def make_hab_from_tod(tod_task):
    new_hab = {'type':'todo'}
    new_hab['text'] = tod_task.name
    try:
        dateListed = list(tod_task.task_dict['due_date_utc'])
        dueNow = str(parser.parse(dateListed).date())
    except:
        dueNow = ''
        
    new_hab['date'] = dueNow
    new_hab['alias'] = tod_task.id
    if tod_task.priority == 1:
        new_hab['priority'] = 2
    elif tod_task.priority == 2:
        new_hab['priority'] = 1.5
    elif tod_task.priority == 3:
        new_hab['priority'] = 1
    elif tod_task.priority == 4:
        new_hab['priority'] = 1
    finished = HabTask(new_hab)
    return finished

def sync_hab2todo(hab, tod):
    habDict = hab.task_dict
    if tod.priority == 1:
        habDict['priority'] = 2
    elif tod.priority == 2:
        habDict['priority'] = 1.5
    else:
        habDict['priority'] = 1
    
    try:
        date = list(tod_task.task_dict['due_date_utc'])
        date_trim = date[0:15]
        dueNow = ''.join(date_trim)
    except:
        dueNow = ''
    
    if hab.date != dueNow:
        habDict['date'] = dueNow
    
    new_hab = HabTask(habDict)
    return new_hab

def update_hab(hab):
    import requests
    import json
    auth = get_started('auth.cfg')
    url = 'https://habitica.com/api/v3/tasks/'
    url += hab.task_dict['id']
    data = json.dumps(hab.task_dict)
    r = requests.put(headers=auth, url=url, data=data)
    return r    

def complete_hab(hab):
    import requests
    import json
    auth = get_started('auth.cfg')
    url = 'https://habitica.com/api/v3/tasks/'
    url += hab.task_dict['id']
    url += '/score/up/'
    hab_dict = hab.task_dict
    hab_dict['completed'] = True
    data = json.dumps(hab_dict)
    r = requests.post(headers=auth, url=url, data=data)
    return r    
 
def get_uniqs(matchDict,tod_tasks,hab_tasks):
    tod_uniq = []
    hab_uniq = []
    
    for tod in tod_tasks:
        tid = tod.id
        if tod.complete == 0:
            if tid not in matchDict.keys():
                tod_uniq.append(tod)
    
    for hab in hab_tasks:
        tid = int(hab.alias)
        if tid not in matchDict.keys():
            hab_uniq.append(hab)
    
    return tod_uniq, hab_uniq

def write_hab_task(task): 
    """
    writes a task, if inserted, to Habitica API as a todo. 
    To be added: functionality allowing you to specify things like difficulty
    """
    import requests
    import json
    auth = get_started('auth.cfg')
    url = 'https://habitica.com/api/v3/tasks/user/'
#    hab = json.dumps(task)
    r = requests.post(headers=auth, url=url, data=task)
    return r

def get_hab_fromID(tid):
    import requests
    import json
    auth = get_started('auth.cfg')
    url = 'https://habitica.com/api/v3/tasks/'
    url += str(tid)
    r = requests.get(headers=auth, url=url)
    task = r.json()
    hab = HabTask(task['data'])
    return hab

def add_hab_id(tid,hab): 
    import requests
    import json
    auth = get_started('auth.cfg')
    url = 'https://habitica.com/api/v3/tasks/'
    hab.task_dict['alias'] = str(tid)
    url += hab.task_dict['id']
    data = json.dumps(hab.task_dict)
    r = requests.put(headers=auth, url=url, data=data)
    return r
    
def delete_hab(hab):
    import requests
    import json
    auth = get_started('auth.cfg')
    url = 'https://habitica.com/api/v3/tasks/'
    url += hab.task_dict['id']
    r = requests.delete(headers=auth, url=url)
    return r
    
def update_tod_matchDict(tod_tasks, matchDict):
    tid_list = []
    for tod in tod_tasks:
        tid_list.append(tod.id)
        if tod.id in matchDict.keys():
            matchDict[tod.id]['tod'] = tod
    for tid in matchDict.keys():
        if tid not in tid_list:
            matchDict.pop(tid)
            
    return matchDict

def update_hab_matchDict(hab_tasks, matchDict):
    from main import delete_hab
    tid_list = []
    for hab in hab_tasks: 
        if 'alias' in hab.task_dict.keys():
            tid = int(hab.alias)
            tid_list.append(tid)
            if tid in matchDict.keys():
                matchDict[tid]['hab'] = hab        
    expired_tids = []
    for tid in matchDict:
        hab = matchDict[tid]['hab']
        if tid not in tid_list:
            expired_tids.append(tid)
    for tid in expired_tids:
        matchDict.pop(tid)
    return matchDict

def get_started(configfile):
    """Get Habitica authentication data from the AUTH_CONF file."""

    logging.debug('Loading habitica auth data from %s' % configfile)

    try:
        cf = open(configfile)
    except IOError:
        logging.error("Unable to find '%s'." % configfile)
        exit(1)

    config = configparser.SafeConfigParser()
    config.readfp(cf)

    cf.close()

    # Get data from config
    rv = {}
    try:
        rv = {'url': config.get('Habitica', 'url'),
              'x-api-user': config.get('Habitica', 'login'),
              'x-api-key': config.get('Habitica', 'password')}

    except configparser.NoSectionError:
        logging.error("No 'Habitica' section in '%s'" % configfile)
        exit(1)

    except configparser.NoOptionError as e:
        logging.error("Missing option in auth file '%s': %s"
                      % (configfile, e.message))
        exit(1)

    # Return auth data as a dictionnary
    return rv
    
def check_matchDict(matchDict):
    """Troubleshooting"""
    for t in matchDict:
        if matchDict[t].complete == 0:
            if t.completed == False:
                print("both undone")
            elif t.completed == True:
                print("hab done, tod undone")
            else: 
                print("something is wroooong check hab %s" % t)
        elif matchDict[t].complete == 1:
            if t.completed == False:
                print("hab undone, tod done")
                print(t.name)
            elif t.completed == True:
                print("both done")
            else:
                print("something is weird check hab %s" % t)
        else:
            print("something is weird check tod %s" % t)

