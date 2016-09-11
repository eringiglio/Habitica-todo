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

from dates import parse_date_utc
from task import CharacterAttribute, ChecklistItem, Difficulty, Task

class HabTask(object):
    def __init__(self, task_dict=None):
        """ Initialise the task.

        Args:
            task_dict (dict): the Todoist task dictionary, as released by task_all.
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
    def id(self):
        """ Task id """
        return self.__task_dict['_id']

    @property
    def name(self):
        """ Task name """
        return self.__task_dict['text']

    @name.setter
    def name(self, name):
        """ Task name """
        self.__task_dict['text'] = name

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
        datestr = self.__task_dict.get('date', None)
        if datestr:
            return parse_date_utc(datestr, milliseconds=True)
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
