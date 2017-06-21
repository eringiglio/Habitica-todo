#!/usr/bin/env python
from hab_task import HabTask
import sys, getopt
import main
import requests

def run_task():
    import main
    from habitsUpdating import get_all_habits
    auth = main.get_started('auth.cfg')
    habits, response = get_all_habits(auth)
    for i in range(len(habits)):
        print('[%s] %s'% (i, habits[i].name))

    raw_updating = raw_input("Which habit would you like to complete? Please give me the number.    ")
    try:
        updating = int(raw_updating)
    except:
        print("I'm sorry, I need you to print just the number, please. Try again!")

    raw_number = raw_input("How many times would you like me to update it?    ")
    try:
        number = int(raw_number)
    except:
        print("I'm sorry, I need you to print just the number, please. Try again!")
    habit = habits[updating]
    rList = []
    for i in range(number):
        r = main.complete_hab(habit)
        rList.append(r)
    return rList


def get_all_habits(auth):
    url = 'https://habitica.com/api/v3/tasks/user/'
    response = requests.get(url,headers=auth)
    hab_raw = response.json()
    hab_tasklist = hab_raw['data'] #FINALLY getting something I can work with... this will be a list of dicts I want to turn into a list of objects with class hab_tasks. Hrm. Weeeelll, if I make a class elsewhere....
    
    #keeping records of all our tasks
    hab_tasks = [] 
    
    #No habits right now, I'm afraid, in hab_tasks--Todoist gets upset. So we're going to make a list of dailies and todos instead...
    for task in hab_tasklist: 
        item = HabTask(task)
        if item.category == 'habit':
            hab_tasks.append(item)
    return(hab_tasks, response)


'''
def main(argv):
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print 'test.py -i <inputfile> -o <outputfile>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'test.py -i <inputfile> -o <outputfile>'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg
   print 'Input file is "', inputfile
   print 'Output file is "', outputfile

if __name__ == "__main__":
   main(sys.argv[1:])
   '''