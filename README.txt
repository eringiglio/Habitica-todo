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

I'm working on getting this up on pip, which I have not yet done before. In the meantime, this is probably best installed by downloading the whole folder and running "python oneWaySync" in the command line. 

This should no longer require either pytodoist nor any existing habitica api program that needs to be installed ahead of time. 

TASK DIFFICULTY
I originally felt that it would be good if task difficulty translated between tasks created on Todoist and 
Habitica. Therefore, task difficulty should sync with the following code by default, as laid out in $PRIORITY_DOC:

Todoist priority			Habitica difficulty
p1							Hard
p2							Medium
p3							Easy
p4							Trivial

If you'd like to change how the sync interprets difficulty or priority, please edit $PRIORITY_DOC. For example, my personal setup actually includes 
translating Todoist p4 to Easy, rather than Trivial, because I find that Trivial yields so few rewards they aren't worth it to me. 

USAGE

INSPIRATION
I'd like to credit several existing apps that I pulled from in order to create this. Notably: 
-philadams' existing habitica app, for a lot of initial code and many helpful explanations of how to do things 
	also for existing API! 
-Pytodoist 
-Dee Dee whose scriptabit which provided a lot of ideas 



THANKS 
