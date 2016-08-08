#!/usr/bin/env python
"""
Let's see if I can just pull tasks from a todoist to a habitica account to start
Functionality to add: 
    syncing difficulty levels btwn tasks
    bidirectional syncing
    creation date syncing????

"""

#Python library imports - this will be functionalities I want to shorten
import habitica #Note: you will want to get a version with API 3 support. At the time of this writing, check submitted pulls on the Github. 
import requests
from pytodoist import todoist
from subprocess import call # useful for running command line commands in python
from urllib2 import urlopen
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
tod_names = []

#Telling the site where the config stuff for Habitica can go and get a list of habitica tasks...
auth, hbt = main.get_started('auth.cfg')  
hab_names =  main.get_task_names(hbt)

#Todoist tasks are, I think, classes. Let's try an alternate way of getting the tasks I want....
url = 'https://habitica.com/api/v3/tasks/user/'
response = requests.get(url,headers=auth)
hab_tasks = response.json()

#Okay, now I need a list of todoist tasks. How do achieve that. 
tod_tasks = tod_user.get_tasks()
for task in tod_tasks: 
	tod_names.append(task.content)

	

#For all the tasks that DO have an analog in both services
for task in shared_tasks: 
	tod_completion = {'text':}
	hab_completion = {'text': task, '}
	if hab_completion = tod_completion:
		pass 
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





