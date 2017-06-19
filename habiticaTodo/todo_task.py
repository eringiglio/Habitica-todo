# -*- coding: utf-8 -*-
""" Implements a Todoist synchronisation task.
"""
# Ensure backwards compatibility with Python 2
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals)
from builtins import *
from datetime import datetime
from tzlocal import get_localzone


#from .dates import parse_date_utc
#from .task import CharacterAttribute, ChecklistItem, Difficulty, Task

"""
So what if I did todoist work a sliiiightly different way, using all my task IDs?
"""

class TodTask(object):
    def __init__(self, task_dict=None):
        """ Initialise the task.

        Args:
            task_dict (dict): the Todoist task dictionary, as released by task_all.
        """
        super().__init__()

        if not task_dict:
            task_dict = {'text': 'scriptabit todo'}

        if not isinstance(task_dict, dict):
            raise TypeError(type(task_dict))

        self.__task_dict = task_dict
    
    @property
    #Get the task dictionary as is
    def task_dict(self):
        return self.__task_dict

    @property
    #Is this task recurring?
    def recurring(self):
        if self.__task_dict['date_string'] == None:
            return 'No'
        elif 'ev' in self.__task_dict['date_string']:
            return  'Yes'
        else:
            return 'No'

    @property
    #Get the task dictionary as is
    def recurring_type(self):
        if reg in self.__task_dict['date_string']:
            return  'daily'
        else:
            return 'weekly'


    @property
    #Get task ID
    def id(self):
        return self.__task_dict['id']

    @property
    #task name
    def history(self):
        import main
        tod_user = main.tod_login('auth.cfg')
        activity = tod_user.activity.get(object_type='item', object_id = self.__task_dict['id'], event_type='completed')
        return activity
        
    @property
    #task name
    def name(self):
        return self.__task_dict['content']
    
    @property
    #date task was added to todoist
    def date_added(self):
        return self.__task_dict['date_added']

    @property
    #priority of task
    def priority(self):
        return self.__task_dict['priority']

    @property
    #difficulty: priority of task rendered to be compatible with habtask
    def hardness(self):
        diffID = self.__task_dict['priority']
        if diffID == 4:
            return "A"
        elif diffID == 3:
            return "B"
        elif diffID == 2:
            return "C"
        else: 
            return "C"

    @property
    #is task complete? 0 for no, 1 for yes
    def complete(self):
        return self.__task_dict['checked']
    
    @complete.setter
    def complete(self, status):
        self.__task_dict['checked'] = status
    
    @property
    #due date
    def due_date(self):
        return self.__task_dict['due_date_utc']
    
    @due_date.setter
    def due_date(self, date):
        self.__task_dict['due_date_utc'] = date
    
    @property
    #due date
    def due(self):
        from dateutil import parser
        import datetime
        if self.__task_dict['due_date_utc'] != None:
            date = parser.parse(self.__task_dict['due_date_utc'])
            return date
        else:
            return ''
    
    @property
    #is it due TODAY?
    def dueToday(self):
        from dateutil import parser
        from datetime import datetime
        from datetime import timedelta
        import pytz
        today = datetime.utcnow().replace(tzinfo=pytz.UTC)
        try:
            wobble = parser.parse(self.__task_dict['due_date_utc']) - timedelta(hours=6) #that datetime thing is pulling todoist's due dates to my time zone
            dueDate = wobble.date()
        except:
            dueDate = ""
            
        if today.date() >= dueDate:
            return 'Yes'
        elif dueDate == "":
            return "No due date"
        else:
            return 'No'

    
    @property
    #date in string form
    def date_string(self):
        return self.__task_dict['date_string']
    
    @property
    #should it be due today?
    def dueLater(self):
        from dateutil import parser
        import datetime
        import pytz
        today = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
        try:
            wobble = parser.parse(self.__task_dict['due_date_utc'])
            dueDate = wobble.date()
        except:
            dueDate = ""
            
        if today.date() == dueDate:
            return 'Yes'
        elif dueDate == "":
            return "No due date"
        else:
            return 'No'

    