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
    #Get task ID
    def id(self):
        return self.__task_dict['id']

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
    #is task complete? 0 for no, 1 for yes
    def complete(self):
        return self.__task_dict['checked']
    
    @property
    #due date
    def due_date(self):
        return self.__task_dict['due_date_utc']
    
    

    