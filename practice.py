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
import requests
from pytodoist import todoist
from subprocess import call # useful for running command line commands in python
from urllib2 import urlopen
from habitica import core
from os import path # will let me call files from a specific path

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
TodTaskList = []

#Telling the site where the config stuff for Habitica can go......
file_path = path.expanduser('~/habitica/auth.cfg')
auth = open(file_path)

#And here's where my Habitica API keys are gonna go.
core.load_auth(auth)


#Okay, now I need a list of todoist tasks. How do achieve that. 
tod_tasks = tod_user.get_tasks()
for task in tod_tasks: #not sure this is necessary 
	TodTaskList.append(task.content.encode("ascii"))

#Now, let's get a list of habitica tasks. We want to look at all of them by name
#regardless of habit, todo, and weekly


\

#Now we'll want to check each task in habitica against the todoist ones... uh, fuck, how do I do this 

#For all the tasks that DO have an analog in both services: 
""""
Note, this section will need proper writing--this is all conceptual at the moment
"""
for task in : 
	if TOD.complete = HAB.complete:
		end
	else: #NOTE this will need to be written properly in code
		TOD.complete = complete
		HAB.complete = complete 
	


#Pulling all the todoist tasks with no habitica equivalent
Tod_uniq_tasks: list(set(TodTaskList) - set(HabTaskList))



for task in tod_tasks: if TOD is HAB:
	#If we do find a match, check status in both programs
	if : 
		#If we find that status agrees, end
		
	#If we find status does not agree, mark task completed
	else: 
		call(["habitica"])

	#If the task in habitica is not found in todoist, make a task in habitica. Default to to-do unless repeating
	if #task in todoist repeated more often than 	

		
		
#Here's where I want Hab tasks to go by default
inbox = todo_user.get_project('Inbox')





