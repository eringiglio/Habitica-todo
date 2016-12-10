# -*- coding: utf-8 -*-
""" Habitica API service interface.
"""

# Ensure backwards compatibility with Python 2
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals)
from builtins import *

import logging
from enum import Enum

import requests



class HabiticaTaskTypes(Enum):
    """ Habitica task types """
    habits = 'habits'
    dailies = 'dailys'
    todos = 'todos'
    rewards = 'rewards'
    completed_todos = 'completedTodos'

class HabiticaService(object):
    """ Habitica API service interface. """
    def __init__(self, headers, base_url):
        """
        Args:
            headers (dict): HTTP headers.
            base_url (str): The base URL for requests.
            """
        self.__headers = headers
        self.__base_url = base_url

    def __delete(self, command, params=None):
        """Utility wrapper around a HTTP DELETE"""
        url = self.__base_url + command
        logging.getLogger(__name__).debug('DELETE %s', url)
        return requests.delete(url, params=params, headers=self.__headers)

    def __get(self, command, params=None):
        """Utility wrapper around a HTTP GET"""
        url = self.__base_url + command
        logging.getLogger(__name__).debug('GET %s', url)
        return requests.get(url, params=params, headers=self.__headers)

    def __put(self, command, data):
        """Utility wrapper around a HTTP PUT"""
        url = self.__base_url + command
        logging.getLogger(__name__).debug('PUT %s', url)
        return requests.put(url, headers=self.__headers, data=data)

    def __post(self, command, data=None):
        """Utility wrapper around a HTTP POST"""
        url = self.__base_url + command
        logging.getLogger(__name__).debug('PUT %s', url)
        return requests.post(url, headers=self.__headers, json=data)

    @staticmethod
    def __get_key(task):
        """ Gets the key from the task ID or alias.
        Preference is given to the ID.

        Args:
            task (dict): The task.

        Returns:
            str: The key

        Raises:
            ValueError: ID or alias not present in task.
        """
        key = task.get('_id', None)
        if not key:
            key = task.get('alias', None)
        if not key:
            raise ValueError('The task must specify an id or alias')
        return key

    def is_server_up(self):
        """Check that the Habitica API is reachable and up

        Returns:
            bool: `True` if the server is reachable, otherwise `False`.
        """
        response = self.__get('status')
        if response.status_code == requests.codes.ok:
            return response.json()['data']['status'] == 'up'
        return False

    def get_user(self):
        """Gets the authenticated user data.

        Returns:
            dict: The user data.
        """
        response = self.__get('user')
        response.raise_for_status()
        return response.json()['data']

    def get_stats(self):
        """Gets the authenticated user stats.

        Returns:
            dict: The stats.
        """
        return self.get_user()['stats']

    def get_tasks(self, task_type=None):
        """Gets all tasks for the current user.

        Args:
            task_type (HabiticaTaskTypes): The type of task to get.
                Default is all tasks.

        Returns:
            dict: The tasks.
        """
        params = {'type': task_type.value} if task_type else {}
        response = self.__get('tasks/user', params)
        response.raise_for_status()
        return response.json()['data']

    def create_task(self, task, task_type=HabiticaTaskTypes.todos):
        """ Creates a task.

        Args:
            task (dict): The task.
            task_type (HabiticaTaskTypes): The type of task to create.
                Default is to create a new todo. Only used if the task['type']
                is empty or not present.

        Returns:
            dict: The new task as returned from the server.
        """
        if not task.get('type', None):
            _type = 'todo'
            if task_type == HabiticaTaskTypes.dailies:
                _type = 'daily'
            elif task_type == HabiticaTaskTypes.habits:
                _type = 'habit'
            elif task_type == HabiticaTaskTypes.rewards:
                _type = 'reward'
            task['type'] = _type

        response = self.__post('tasks/user', task)
        response.raise_for_status()
        return response.json()['data']

    def create_tasks(self, tasks):
        """ Creates multiple tasks.

        Note that unlike HabiticaService.create_task, this method
        **does not** check that the task type is valid.

        Args:
            task (list): The list of tasks.

        Returns:
            list: The new tasks as returned from the server.
        """
        response = self.__post('tasks/user', tasks)
        response.raise_for_status()
        return response.json()['data']

    def get_task(self, _id='', alias=''):
        """ Gets a task.

        If both task ID and alias are specified, then the ID is used.

        Args:
            _id (str): The task ID.
            alias (str): The task alias.

        Returns:
            dict: The task, or None if the task is not found.

        Raises:
            ValueError
        """
        key = _id if _id else alias
        if not key:
            raise ValueError('Neither ID or alias specified')

        response = self.__get('tasks/{key}'.format(key=key))
        if response.status_code == requests.codes.ok:
            return response.json()['data']
        else:
            return None

    def delete_task(self, task):
        """ Delete a task.

        Args:
            task (dict): The task.
        """
        response = self.__delete('tasks/{0}'.format(task['_id']))
        response.raise_for_status()

    def update_task(self, task):
        """ Updates an existing task.

        Args:
            task (dict): The task.

        Returns:
            dict: The new task as returned from the server.

        Raises:
            ValueError: if neither an ID or alias are present in task.
        """
        key = self.__get_key(task)
        response = self.__put('tasks/{0}'.format(key), task)
        response.raise_for_status()
        return response.json()['data']

    def score_task(self, task, direction='up'):
        """ Score a task.

        Args:
            task (dict): the task to score.
            direction (str): 'up' or 'down'

        Returns:
            dict: Habitica API response data.

        Raises:
            ValueError: invalid direction.
            ValueError: missing ID or alias.
        """
        key = self.__get_key(task)
        response = self.__post(
            'tasks/{0}/score/{1}'.format(key, direction),
            data=None)
        response.raise_for_status()
        return response.json()['data']

    def upsert_task(self, task, task_type=HabiticaTaskTypes.todos):
        """Upserts a task.

        Existing tasks will be updated, otherwise a new task will be created.

        Args:
            task (dict): The task.
            task_type (HabiticaTaskTypes): The type of task to create if a new
                task is required. Can be overriden by an existing task['type']
                value.

        Returns:
            dict: The new task as returned from the server.

        Raises:
            ValueError
        """
        key = task.get('_id', None)
        if not key:
            key = task.get('alias', None)
        if not key:
            raise ValueError('The task must specify an id or alias')

        # Does the task already exist?
        if self.get_task(key):
            logging.getLogger(__name__).debug('task %s exists, updating', key)
            response = self.__put('tasks/{0}'.format(key), task)
            response.raise_for_status()
            return response.json()['data']
        else:
            logging.getLogger(__name__).debug(
                'task %s not found, creating', key)
            return self.create_task(task, task_type)

    # I don't think the API lets me set partial user objects in this way.
    # So I could get the entire user structure, swap the stats for the argument
    # version, and then PUT that back. Or I can wait to see if I even need this
    # method at all.
    # def set_stats(self, stats):
    # """Sets the authenticated user stats.
    # ** Not implemented **
    # Note that unlike the fine-grained set_[hp|mp|xp] methods,
    # this method performs no sanity checking of values.

        # Args:
        # stats (dict): The stats to set. This can be a
        # partial set of values.

        # Returns: dictionary: The new stats, as returned by the server.

        # Raises: NotImplementedError
        # """
        # raise NotImplementedError
        # response = self.__put('user', {'stats': stats})
        # if response.status_code == requests.codes.ok:
        # return response.json()['data']['stats']
        # return None

    def set_hp(self, hp):
        """ Sets the user's HP.

        Args:
            hp (float): The new HP value.

        Returns:
            float: The new HP value, extracted from the JSON response data.
        """
        if hp > 50:
            raise ArgumentOutOfRangeError("hp > 50")
        if hp < 0:
            raise ArgumentOutOfRangeError("hp < 0")

        response = self.__put('user', {'stats.hp': hp})
        response.raise_for_status()
        return response.json()['data']['stats']['hp']

    def set_mp(self, mp):
        """ Sets the user's MP (mana points).

        Args:
            mp (float): The new MP value.

        Returns:
            float: The new MP value, extracted from the JSON response data.
        """
        max_mp = self.get_user()['stats']['mp']
        if mp > max_mp:
            raise ArgumentOutOfRangeError("mp > {0}".format(max_mp))
        if mp < 0:
            raise ArgumentOutOfRangeError("mp < 0")

        response = self.__put('user', {'stats.mp': mp})
        response.raise_for_status()
        return response.json()['data']['stats']['mp']

    def set_exp(self, exp):
        """ Sets the user's XP (experience points).

        Args:
            exp (float): The new XP value.

        Returns:
            float: The new XP value, extracted from the JSON response data.
        """
        if exp < 0:
            raise ArgumentOutOfRangeError("exp < 0")

        response = self.__put('user', {'stats.exp': exp})
        response.raise_for_status()
        return response.json()['data']['stats']['exp']

    def set_gp(self, gp):
        """ Sets the user's gold (gp).

        Args:
            gp (float): The new gold value.

        Returns:
            float: The new gold value, extracted from the response data.
        """
        if gp < 0:
            raise ArgumentOutOfRangeError("gp < 0")

        response = self.__put('user', {'stats.gp': gp})
        response.raise_for_status()
        return response.json()['data']['stats']['gp']

    def get_tags(self):
        """ Get the current user's tags.

        Returns:
            list: The tags.
        """
        response = self.__get('tags')
        response.raise_for_status()
        return response.json()['data']

    def create_tag(self, name):
        """ Create a tag.

        Args:
            name (str): the tag name.

        Returns:
            dict: The new tag.
        """
        response = self.__post('tags', data={'name': name})
        response.raise_for_status()
        return response.json()['data']

    def create_tags(self, tags):
        """ Create the tags. Existing tags are ignored.

        Args:
            tags (list): The list of tag names.

        Returns:
            list: The list of Habitica Tag objects corresponding to
            the tags argument.
        """
        current_tags = self.get_tags()
        current_tag_names = [t['name'] for t in current_tags]
        return_tags = [t for t in current_tags if t['name'] in tags]
        for required in tags:
            if required not in current_tag_names:
                return_tags.append(self.create_tag(required))

        return return_tags

    def delete_checklist_item(self, task_id, item_id):
        """ Delete a checklist item.

        Args:
            task_id (str): The task ID.
            item_id (str): The checklist item ID.
        """
        response = self.__delete(
            'tasks/{0}/checklist/{1}'.format(task_id, item_id))
        response.raise_for_status()

    def create_checklist_item(self, task_id, item):
        """ Add a checklist item to the task.

        Args:
            task_id (str): The task ID.
            item (dict): The new checklist item.
        """
        response = self.__post(
            'tasks/{0}/checklist'.format(task_id),
            data=item)
        response.raise_for_status()

    def feed_pet(self, pet, food):
        """ Feed a pet.

        Args:
            pet (str): The pet name.
            food (str): The food.

        Returns:
            dict: The Habitica response data.
        """
        response = self.__post('user/feed/{0}/{1}'.format(pet, food))
        response.raise_for_status()
        return response.json()

    def hatch_pet(self, egg, potion):
        """ Hatch a pet.

        Args:
            egg (str): The egg name.
            potion (str): The potion name.

        Returns:
            dict: The Habitica response data.
        """
        response = self.__post('user/hatch/{0}/{1}'.format(egg, potion))
        response.raise_for_status()
        return response.json()
