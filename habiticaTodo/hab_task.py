# -*- coding: utf-8 -*-
""" Implements a Habitica synchronisation task.
This is borrowed essentially wholesale from scriptabit by DeeDee (see README).
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
import time
import pytz

from dates import parse_date_utc
from task import CharacterAttribute, ChecklistItem, Difficulty, Task

class HabTask(object):
    def __init__(self, task_dict=None):
        """ Initialise the task.

        Args: task_dict (dict): the Todoist task dictionary, as released by task_all.
        """
        super().__init__()

        if not task_dict:
            task_dict = {'text': 'Todoist todo'}

        if not isinstance(task_dict, dict):
            raise TypeError(type(task_dict))

        self.__task_dict = task_dict

        if 'priority' not in task_dict:
            task_dict['priority'] = Difficulty.default.value

        if 'attribute' not in task_dict:
            task_dict['attribute'] = CharacterAttribute.default.value

        # The Habitica API chokes if you attempt to update a task with a
        # checklist in the request data. To work around this we move the
        # checklist (if any) out of task_dict so it can be handled separately.
        # We also need separate API calls for deleted, added, and updated
        # checklist items items
        self.new_checklist_items = []
        if 'checklist' in task_dict.keys():
            self.existing_checklist_items = task_dict['checklist']
            del task_dict['checklist']
        else:
            self.existing_checklist_items = []

    @property
    def task_dict(self):
        """ Gets the internal task dictionary. """
        return self.__task_dict

    @property
    def due(self):
        """ returns UTC due date """
        from dateutil import parser
        import datetime
        if self.__task_dict['type'] == 'todo' and self.__task_dict['date'] != '':
            date = parser.parse(self.__task_dict['date'])
            return date
        else:
            return ''
        
    @property
    #When will this recurring task next be due?
    def starting(self):
        if self.__task_dict['type'] == 'daily':
            start = self.__task_dict['startDate']
        else:
            start = ''
    
    @starting.setter
    def starting(self, starting):
        """ Task name """
        self.__task_dict['startDate'] = starting
    
    @property
    #Is this a weekly daily or something that repeats every X days?
    def rep_pattern(self):
        if self.__task_dict['type'] == 'daily':
            return self.__task_dict['frequency']
        else:
            return ''
   
    @rep_pattern.setter
    def rep_pattern(self, rep):
        """ Task name """
        self.__task_dict['frequency'] = rep
   
    @property
    #What days of the week does this daily repeat--or in how many days?
    def dailies_due(self):
        if self.__task_dict['type'] == 'daily':
            if self.__task_dict['frequency'] == 'weekly':
                days = ['ev ']
                if self.__task_dict['repeat']["m"] == True:
                        days.append("monday")
                if self.__task_dict['repeat']["t"] == True:
                        days.append("tuesday")
                if self.__task_dict['repeat']["w"] == True:
                        days.append("wednesday")
                if self.__task_dict['repeat']["th"] == True:
                        days.append("thursday")
                if self.__task_dict['repeat']["f"] == True:
                        days.append("friday")
                if self.__task_dict['repeat']["s"] == True:
                        days.append("saturday")
                if self.__task_dict['repeat']["su"] == True:
                        days.append("sunday")
                days.append(', ')
                days.pop()
                due_dates = ''.join(days)
                return due_dates
            else:
                dayCycle = self.__task_dict['everyX']
                return dayCycle
        else:
            return ''
    
    @property
    #Is this task due today?
    def due_now(self):
        now = time.strftime()
        if self.__task_dict['type'] == 'daily':
            return ''
        else:
            return ''

    @property
    #is task complete? 0 for no, 1 for yes
    def complete(self):
        return self.__task_dict['checked']
    
    @property
    def id(self):
        """ Task id """
        return self.__task_dict['_id']

    @property
    #difficulty: priority of task rendered to be compatible with habtask
    def hardness(self):
        diffID = self.__task_dict['priority']
        if diffID == 2:
            return "A"
        elif diffID == 1.5:
            return "B"
        elif diffID == 1:
            return "C"
        else: 
            return "D"


    @property
    def name(self):
        """ Task name """
        return self.__task_dict['text']

    @name.setter
    def name(self, name):
        """ Task name """
        self.__task_dict['text'] = name
    
    @property
    def alias(self):
        """ Task name """
        return self.__task_dict['alias']

    @property
    def date(self):
        """ Task name """
        if  self.__task_dict['type'] == 'todo':
            try:
                return self.__task_dict['date']
            except:
                return ''
        else:
            return self.__task_dict['startDate']

    @property
    def dueToday(self):
        """This is intended to tell us if a given daily is due today or not."""
        from datetime import datetime
        from dateutil import parser
        local_tz = get_localzone()
        raw_now = datetime.now()
        now = raw_now.replace(tzinfo=pytz.utc).astimezone(local_tz).date()
        if self.__task_dict['type'] == 'daily':
            datestr = self.__task_dict['startDate']
            startDate = parser.parse(datestr).date()
            type = self.__task_dict['frequency']
            
            if startDate >= now:
                return False
            elif type == 'weekly':
                
                weekDay = now.weekday()
                if weekDay == 0:
                    return (self.__task_dict['repeat']['m'])
                elif weekDay == 1:
                    return (self.__task_dict['repeat']['t'])
                elif weekDay == 2:
                    return (self.__task_dict['repeat']['w'])
                elif weekDay == 3:
                    return (self.__task_dict['repeat']['th'])
                elif weekDay == 4:
                    return (self.__task_dict['repeat']['f'])
                elif weekDay == 5:
                    return (self.__task_dict['repeat']['s'])
                elif weekDay == 6:
                    return (self.__task_dict['repeat']['su'])
                else:
                    return "Error: what day is it" 
            elif type == 'daily':
                evXdays = self.__task_dict['everyX']
                if evXdays > 1:
                    daysSinceStart = now - startDate
                    return (daysSinceStart.days % evXdays == 0)                    
                else:
                    return True                    
            else:
                return "Error: check your daily?"
        else:
            return 'TODO, NA'

    @property
    def category(self):
        """ Task type """
        return self.__task_dict['type']

    @category.setter
    def category(self, name):
        """ Task name """
        self.__task_dict['type'] = name        

    @property
    def description(self):
        """ Task description """
        return self.__task_dict['notes']

    @description.setter
    def description(self, description):
        """ Task description """
        self.__task_dict['notes'] = description

    @property
    def completed(self):
        """ Task completed """
        return self.__task_dict['completed']

    @completed.setter
    def completed(self, completed):
        """ Task completed """
        self.__task_dict['completed'] = completed

    @property
    def difficulty(self):
        """ Task difficulty """
        return Difficulty.from_value(self.__task_dict['priority'])

    @difficulty.setter
    def difficulty(self, difficulty):
        """ Task difficulty """
        if not isinstance(difficulty, Difficulty):
            raise TypeError
        self.__task_dict['priority'] = difficulty.value

    @property
    def attribute(self):
        """ Task character attribute """
        return CharacterAttribute.from_value(self.__task_dict['attribute'])

    @attribute.setter
    def attribute(self, attribute):
        """ Task character attribute """
        if not isinstance(attribute, CharacterAttribute):
            raise TypeError
        self.__task_dict['attribute'] = attribute.value

    @property
    def due_date(self):
        """ The due date if there is one, or None. """
        from dates import parse_date_utc
        datestr = self.__task_dict.get('date', None)
        if datestr:
            return parse_date_utc(datestr, milliseconds=True)
        else:
            return None

    @due_date.setter
    def due_date(self, due_date):
        """ Sets or clears the due date. """
        if due_date and not isinstance(due_date, datetime):
            raise TypeError
        if due_date:
            self.__task_dict['date'] = \
                due_date.astimezone(get_localzone()).date()
        elif 'date' in self.__task_dict:
            del self.__task_dict['date']

    @property
    def last_modified(self):
        """ The last modified timestamp in UTC. """
        timestamp = self.__task_dict['updatedAt']
        if timestamp:
            return parse_date_utc(timestamp)

    @property
    def checklist(self):
        """ The checklist.

        Returns:
            list: The checklist, or an empty list if there are no
                checklist items.
        """
        checklist = []

        for i in self.new_checklist_items:
            checklist.append(ChecklistItem(
                name=i['text'],
                checked=i['completed']))

        for i in self.existing_checklist_items:
            checklist.append(ChecklistItem(
                name=i['text'],
                checked=i['completed']))

        return checklist

    @checklist.setter
    def checklist(self, checklist):
        """ Sets, or clears the checklist. """
        for i in checklist:
            # create new item
            self.new_checklist_items.append({
                'text': i.name,
                'completed': i.checked})
