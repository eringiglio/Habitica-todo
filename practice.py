#!/usr/bin/env python
"""
Let's see if I can just pull tasks from a todoist to a habitica account to start
Functionality to add: 
    syncing difficulty levels btwn tasks
    bidirectional syncing
    creation date syncing????

"""

#Python library imports - this will be functionalities I want to shorten
#   as I use them. habitica???
import habitica 
from pytodoist import todoist
from subprocess import call # useful for running command line commands in python

#Authorships, etc
__author__ = "Erin Giglio"
__copyright__ = "Copyright 2016"
__credits__ = ["Erin Giglio"]
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Erin Giglio"
__email__ = "eringiglio@gmail.com"
__status__ = "Development"

#Note: anything for Todoist needs to be prefaced with "tod." Anything for Habitica, "hab."

#Here's where I'm putting my login stuff for Todoist.
tod_user = todoist.login('eringiglio@gmail.com','Liathro1!')
tod_response = tod_api.sync()
TodTaskList = []

#Okay, now I need a list of todoist tasks. How do achieve that. 
tod_tasks = tod_user.get_tasks()
for task in tod_tasks:
	TodTaskList.append(task.content.encode("ascii"))

#Now, let's get a list of habitica tasks. We want to look at all of them by name
#regardless of habit, todo, and weekly
hab_habits = call(["habitica","habits"])
hab_dailies = call(["habitica","dailies"])
hab_todos = call(["habitica", "todos"])

#Now we'll want to check each task in habitica against the todoist ones...


#Here's where I want Hab tasks to go by default
inbox = todo_user.get_project('Inbox')





