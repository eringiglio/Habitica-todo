README

This is intended to be a two-way sync of Habitica and todoist. Any tasks that can't be found 
in both services should appear on the others, with the same status. If you complete a task on one service, 
it should appear as completed on another. Tasks that are created on Habitica should be sent to the 'Inbox' 
project on Todoist. 

AS A NOTE: in order to have two way syncing, you MUST have a paid copy of Todoist. It's not possible for me to port complete tasks from Todoist otherwise. If you do not have a paid copy of Todoist, the following will happen: 

a) completed tasks will not sync between the services
b) tasks that you begin and complete from one service to the other will not transfer between the two.
	That means that if you create a task in todoist and then check it off, right now it will _not_ send the points to Habitica.
	
	I encourage people without paid todoist to pick up todoist-habitrpg, which doesn't care one way or the other. (I rather hope that kusold's success with that means that Habitica-todoist will be able to figure this out eventually, but right now that's my workaround.) Or you could pony up the $30 for a year's subscription of Todoist. I'm pretty sure it's worth it. 

INSTALLATION

You'll want to install two existing API Python wrappers that this utility depends on...

pip install habitica
pip install pytodoist

TASK DIFFICULTY
I felt that it would be good if task difficulty translated between tasks created on Todoist and 
Habitica. Therefore, task difficulty should sync with the following code by default, as laid out in $PRIORITY_DOC:

Todoist priority			Habitica difficulty
p1							Hard
p2							Medium
p3							Easy
p4							Trivial

If you'd like to change how the sync interprets difficulty or priority, please edit $PRIORITY_DOC.

USAGE

INSPIRATION
I'd like to credit several existing apps that I pulled from in order to create this. Notably: 
-philadams' existing habitica app, for a lot of initial code and many helpful explanations of how to do things 
	also for existing API! 
-Pytodoist 
-Dee Dee whose scriptabit which provided a lot of ideas 



THANKS 
