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

VERSION = 'Habitica-todo version 2.1.0'
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
List of utilities and what they do: scroll down for specific things
add_hab_id: 
    used to add a new alias (usually the tod ID number) to a habitica task
check_matchDict: 

check_newMatches: 

clean_matchDict:

complete_hab:

delete_hab: 
    Takes a HabTask object and sends an API call to delete it from the habitica account.
get_all_habtasks:

get_hab_fromID:
    Takes an integer, like a tod ID, and calls hab tasks by that alias from API.
get_started:
    Takes auth document and logs the user into todoist and habitica for active work. 
get_uniqs:

make_daily_from_tod:
    Takes a repeating tod task and turns it into a habitica daily. 
make_hab_from_tod:
    Takes a single tod task and turns it into a habitica todo.
make_tod_from_hab:
    Takes a habitica task and turns it into a todo. Does not sync dueness or repetitiveness; needs updating.
matchDates:

openMatchDict:

openMatchDictTwo:

synchab2todo:

sync_hab2todo_daily:

sync_hab2todo_todo:

syncHistories:

tod_login:

update_hab:

update_hab_matchDict:

update_tod_matchDict:
    
write_hab_task:
    takes HabTask object, writes to habitica API (used to make a new task in habitica)

"""


"""
Small utilities written by me start here.
"""

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

def check_newMatches(matchDict,tod_uniq,hab_uniq):
    from main import add_hab_id, make_tod_from_hab
    matchesHab = []
    matchesTod = []
    for tod in tod_uniq:
        tid = tod.id 
        for hab in hab_uniq:
            if tod.id == hab.alias:
                matchDict[tid] = {}
                matchDict[tid]['tod'] = tod
                matchDict[tid]['hab'] = hab
                matchDict[tid]['recurs'] = tod.recurring
                matchesTod.append(tod)
                matchesHab.append(hab)
        hab_uniqest = list(set(hab_uniq) - set(matchesHab))
        tod_uniqest = list(set(tod_uniq) - set(matchesTod))
        
        for tod_task in tod_uniqest:
            tid = tod_task.id
            if tid not in matchDict.keys():
                for hab_task in hab_uniqest:
                    if tod_task.name == hab_task.name:
                        try:
                            oldTid = int(hab_task.alias)
                        except:
                            oldTid = ''
                        if oldTid in matchDict.keys():
                            matchDict.pop(oldTid)
                        r = add_hab_id(tid,hab_task)
                        if r.ok == False:
                            print("Error updating hab %s! %s" % (hab.name,r.reason))
                        else:
                            matchDict[tid] = {}
                            matchDict[tid]['hab'] = hab_task
                            matchDict[tid]['tod'] = tod_task
                            matchDict[tid]['recurs'] = tod_task.recurring
    return matchDict

def clean_matchDict(matchDict):
    for tid in matchDict:
        if 'recurs' not in matchDict[tid].keys():
            matchDict[tid]['recurs'] = matchDict[tid]['tod'].recurring
        hab = matchDict[tid]['hab']
        tod = matchDict[tid]['tod']
    return matchDict

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

def delete_hab(hab):
    import requests
    import json
    auth = get_started('auth.cfg')
    url = 'https://habitica.com/api/v3/tasks/'
    url += hab.task_dict['id']
    r = requests.delete(headers=auth, url=url)
    return r

def get_all_habtasks(auth):
    #Todoist tasks are, I think, classes. Let's make Habitica tasks classes, too.
    url = 'https://habitica.com/api/v3/tasks/user/'
    response = requests.get(url,headers=auth)
    hab_raw = response.json()
    hab_tasklist = hab_raw['data'] #FINALLY getting something I can work with... this will be a list of dicts I want to turn into a list of objects with class hab_tasks. Hrm. Weeeelll, if I make a class elsewhere....
    
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
    return(hab_tasks, response)

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

def get_uniqs(matchDict,tod_tasks,hab_tasks):
    tod_uniq = []
    hab_uniq = []

    for tod in tod_tasks:
        tid = tod.id
        if tod.complete == 0:
            if tid not in matchDict.keys():
                tod_uniq.append(tod)

    for hab in hab_tasks:
        tid = hab.alias
        if tid not in matchDict.keys():
            print(tid)
            hab_uniq.append(hab)
    
    return tod_uniq, hab_uniq

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
        new_hab['priority'] = '2'
    elif tod.priority == 2:
        new_hab['priority'] = '1.5'
    elif tod.priority == 3:
        new_hab['priority'] = '1'
    elif tod.priority == 4:
        new_hab['priority'] = '1'
        
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
        new_hab['priority'] = '2'
    elif tod_task.priority == 2:
        new_hab['priority'] = '1.5'
    elif tod_task.priority == 3:
        new_hab['priority'] = '1'
    elif tod_task.priority == 4:
        new_hab['priority'] = '1'
    finished = HabTask(new_hab)
    return finished

def make_tod_from_hab(hab):
    project_id = tod_projects[0].data['id']
    tod = {}
    tod['content'] = hab.name
    tod['due_date_utc'] = hab.date
    if hab.priority == '2':
        tod['priority'] = 1
    elif hab.priority == '1.5': 
        tod['priority'] == 2
    elif hab.priority == '1': 
        tod['priority'] == 3
    else:
        tod['priority'] == 4



def matchDates(matchDict):
    '''Error/debugging script to match all hab dates with tod dates.'''
    from main import sync_hab2todo
    for tid in matchDict:
        tod = matchDict[tid]['tod']
        hab = matchDict[tid]['hab']
        try:
            hab_date = parse_date_utc(hab.date).date()
        except:
            hab_date = ''
        
        try:
            tod_date = tod.due.date()
        except:
            tod_date = ''
        
        rList = []
        if tod_date != hab_date:
            print(tod.name)
            newHab = sync_hab2todo(hab,tod)
            r = update_hab(newHab)
            matchDict[tid]['hab'] = newHab
            rList.append(r,hab.name)

def openMatchDict():
    import pickle
    pkl_file = open('oneWay_matchDict.pkl','rb')
    pkl_load = pickle.Unpickler(pkl_file)
    try: 
        matchDict = pkl_load.load()
    except:
        matchDict = {}

    pkl_file.close()
    for tid in matchDict:
        if 'recurs' not in matchDict[tid].keys():
            tod = matchDict[tid]['tod']
            matchDict[tid]['recurs'] = tod.recurring
    return matchDict

def openMatchDictTwo():
    import pickle
    pkl_file = open('twoWay_matchDict.pkl','rb')
    pkl_load = pickle.Unpickler(pkl_file)
    try: 
        matchDict = pkl_load.load()
    except:
        matchDict = {}

    pkl_file.close()
    for tid in matchDict:
        if 'recurs' not in matchDict[tid].keys():
            tod = matchDict[tid]['tod']
            matchDict[tid]['recurs'] = tod.recurring
    return matchDict

def purge_habs(hab_uniq, matchDict):
    hab_uniqest = []
    cruft = []
    for hab in hab_uniq:
        try:
            tid = int(hab.alias)
            cruft.append(hab)
        except:
            hab_uniqest.append(hab)

    return hab_uniqest

def sync_hab2todo(hab, tod):
    if hab.category == 'daily':
        new_hab = sync_hab2todo_daily(hab,tod)
        return new_hab
    elif hab.category == 'todo':
        new_hab = sync_hab2todo_todo(hab,tod)
        return new_hab
    else: 
        print("Error! Hab of incorrect type!")

def sync_hab2todo_daily(hab, tod):
    from dates import parse_date_utc
    from datetime import datetime
    from datetime import timedelta
    import pytz
    habDict = hab.task_dict
    if tod.priority == 4:
        habDict['priority'] = 2
    elif tod.priority == 3:
        habDict['priority'] = 1.5
    else:
        habDict['priority'] = 1

    now = datetime.now().replace(tzinfo=pytz.utc).date()
        
    if hab.due.date() != (tod.due.date() - timedelta(days=1)):
        habDict['startDate'] = str(tod.due.date() - timedelta(days=1))

    newHab = HabTask(habDict)

    return newHab

def sync_hab2todo_todo(hab, tod): 
    from dates import parse_date_utc
    habDict = hab.task_dict
    if tod.priority == 4:
        habDict['priority'] = 2
    elif tod.priority == 3:
        habDict['priority'] = 1.5
    else:
        habDict['priority'] = 1
    
    try:
        dueNow = tod.due.date()
    except:
        dueNow = ''
    try:
        dueOld = parse_date_utc(hab.date).date()
    except:
        dueOld = ''
        
    if dueOld != dueNow:
        habDict['date'] = str(dueNow)
    
    new_hab = HabTask(habDict)
    return new_hab

def syncHistories(matchDict):

    """
    I wanted to see if I could convince recurring habs and tods to sync based on history. 
    Assuming both recur...
    """
    from dates import parse_date_utc
    from dateutil import parser
    from datetime import datetime
    from datetime import timedelta
    from main import complete_hab, update_hab
    from main import tod_login
    tod_user = tod_login('auth.cfg')
    todList = {}
    for tid in matchDict:
        try: 
            matchDict[tid]['recurs']
        except:
            print(tid)
            matchDict[tid]['recurs'] = matchDict[tid]['tod'].recurring
        if matchDict[tid]['recurs'] == 'Yes':
            hab = matchDict[tid]['hab']
            tod = matchDict[tid]['tod']
            habHistory = hab.history
            todHistory = tod.history
            try:
                lastTod = parser.parse(todHistory[0]['event_date']).date()
            except:
                lastTod = tod.due.date()
            habLen = len(habHistory) - 1
            try:
                lastHab = datetime.fromtimestamp(habHistory[habLen]['date']/1000).date() - timedelta(days=1)
            except:
                lastHab = hab.due.date() - timedelta(days=1)
            lastNow = datetime.today().date()
            if lastHab > hab.due.date(): 
                newHab = sync_hab2todo(hab, tod)
                r = update_hab(newHab)
            if lastTod != lastHab:
                if lastHab < lastTod and hab.dueToday == True:
                    print("Updating daily hab %s to match tod" % tod.name)
                    r = complete_hab(hab)
                    print(r)
                elif lastTod < lastHab: # and hab.dueToday == False:
                    if lastTod < lastNow == False:
                        print("Updating daily tod %s to match hab" % tod.name)
                        #fix_tod = tod_user.items.get_by_id(tid)
                        #fix_tod.close() #this to be uncommented in a week or so
                        print(lastTod)
                        print(lastHab)
                        print(lastNow)
                    elif hab.due.date() < lastNow:
                        print("Hey, tod %s looks like it's getting pretty late. Think about tackling that one?" % tod.name)
                        print(lastTod)
                        print(lastHab)
                        print(hab.due)
                else:
                    print("This one doesn't apply, right?")
                    print(tod.name)
                    print(lastTod)
                    print(lastHab)
                    print(hab.due)
    tod_user.commit()
    return matchDict

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

def update_hab(hab):
    import requests
    import json
    from datetime import datetime
    from main import get_started
    auth = get_started('auth.cfg')
    url = 'https://habitica.com/api/v3/tasks/'
    try:
        tag = str(hab.task_dict['alias'])
    except:
        tag = hab.task_dict['id']
    url += tag
    wanted_keys = ['alias', 'text', 'priority','date']
    data = {x : hab.task_dict[x] for x in wanted_keys if x in hab.task_dict}
    r = requests.put(headers=auth, url=url, data=data)
    if r.ok == 'No':
        print(r.text)
    return r
 
def update_hab_matchDict(hab_tasks, matchDict):
    from main import delete_hab 
    from main import sync_hab2todo
    from main import update_hab
    from dates import parse_date_utc
    hardness = []
    tid_list = []
    expired_tids = []
    aliasError = []
    for hab in hab_tasks: 
        if 'alias' in hab.task_dict.keys():
            try:
                tid = int(hab.alias)
                tid_list.append(tid)
            except:
                aliasError.append(hab)
            if tid in matchDict.keys():
                try:
                    date1 = hab.due.date()
                except:
                    date1 = ''
                try: 
                    date2 = matchDict[tid]['hab'].due.date()
                except:
                    date2 = ''
                    
                if date1 != date2 and matchDict[tid]['recurs'] == 'No':
    #if the hab I see and the matchDict don't agree... sync to the todoist task
                    print(date1)
                    print(date2)
                    newHab = sync_hab2todo(hab,matchDict[tid]['tod'])
                    r = update_hab(newHab)
                    print('Dates wrong; updated hab %s !' % hab.name)
                    print(r)

                if hab.hardness != matchDict[tid]['hab'].hardness:
                    print("hardness mismatch!")
                    hardness.append(tid)
                    newHab = sync_hab2todo(hab,matchDict[tid]['tod'])
                    r = update_hab(newHab)
                    print(r)
                    print('Updated hab %s !' % hab.name)

                matchDict[tid]['hab'] = hab
    '''
    for hab in aliasError:
        for tid in matchDict:
            matchHab = matchDict[tid]['hab']
            if hab.name == matchHab.name:
                expired_tids.append(tid)
    '''
    for tid in matchDict:
        hab = matchDict[tid]['hab']
        if tid not in tid_list:
            expired_tids.append(tid)

    for tid in expired_tids:
        if tid not in matchDict.keys():
            continue
        else:
            matchDict.pop(tid)

    return matchDict

def update_tod_matchDict(tod_tasks, matchDict):
    tid_list = []
    for tod in tod_tasks:
        tid_list.append(tod.id)
        if tod.id in matchDict.keys():
            matchDict[tod.id]['tod'] = tod
    for tid in list(matchDict):
        if tid not in tid_list:
            matchDict.pop(tid)
            
    return matchDict

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
