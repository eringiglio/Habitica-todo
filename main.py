#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Habitica command-line interface, adapted from core.py in philadams' habitica. Links below:
Phil Adams http://philadams.net
habitica: commandline interface for http://habitica.com
http://github.com/philadams/habitica

Changes I've made essentially revolve around tweaking a command-line utility running in python
to be a module holding a series of smaller python utilities that can be called within a larger program. 



habitica: commandline interface for http://habitica.com
http://github.com/philadams/habitica

Usage: habitica [--version] [--help]
                <command> [<args>...] [--difficulty=<d>]
                [--verbose | --debug]

    Options:
      -h --help         Show this screen
      --version         Show version
      --difficulty=<d>  (easy | medium | hard) [default: easy]
      --verbose         Show some logging information
      --debug           Some all logging information

    The habitica commands are:
      status                 Show HP, XP, GP, and more
      habits                 List habit tasks
      habits up <task-id>    Up (+) habit <task-id>
      habits down <task-id>  Down (-) habit <task-id>
      dailies                List daily tasks
      dailies done           Mark daily <task-id> complete
      dailies undo           Mark daily <task-id> incomplete
      todos                  List todo tasks
      todos done <task-id>   Mark one or more todo <task-id> completed
      todos add <task>       Add todo with description <task>
      server                 Show status of Habitica service
      home                   Open tasks page in default browser

    For `habits up|down`, `dailies done|undo`, and `todos done`, you can pass
    one or more <task-id> parameters, using either comma-separated lists or
    ranges or both. For example, `todos done 1,3,6-9,11`.
    """

def setup():
	
    # set up args
    args = docopt(cli.__doc__, version=VERSION)

    # set up logging
    if args['--verbose']:
        logging.basicConfig(level=logging.INFO)
    if args['--debug']:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug('Command line args: {%s}' %
                  ', '.join("'%s': '%s'" % (k, v) for k, v in args.items()))

    # Set up auth
    auth = load_auth(AUTH_CONF)

    # Prepare cache
    cache = load_cache(CACHE_CONF)

    # instantiate api service
    hbt = api.Habitica(auth=auth)

    # GET server status
def server():
    server = hbt.status()
    if server['status'] == 'up':
        print('Habitica server is up')
    else:
		print('Habitica server down... or your computer cannot connect')

	# open HABITICA_TASKS_PAGE
def home():
	home_url = '%s%s' % (auth['url'], HABITICA_TASKS_PAGE)
	print('Opening %s' % home_url)
	open_new_tab(home_url)

    # GET user
def status():
	# gather status info
	user = hbt.user()
	party = hbt.groups.party()
	stats = user.get('stats', '')
	items = user.get('items', '')
	food_count = sum(items['food'].values())

	# gather quest progress information (yes, janky. the API
	# doesn't make this stat particularly easy to grab...).
	# because hitting /content downloads a crapload of stuff, we
	# cache info about the current quest in cache.
	quest = 'Not currently on a quest'
	if (party is not None and
			party.get('quest', '') and
			party.get('quest').get('active')):

		quest_key = party['quest']['key']

		if cache.get(SECTION_CACHE_QUEST, 'quest_key') != quest_key:
			# we're on a new quest, update quest key
			logging.info('Updating quest information...')
			content = hbt.content()
			quest_type = ''
			quest_max = '-1'
			quest_title = content['quests'][quest_key]['text']

			# if there's a content/quests/<quest_key/collect,
			# then drill into .../collect/<whatever>/count and
			# .../collect/<whatever>/text and get those values
			if content.get('quests', {}).get(quest_key, {}).get('collect'):
				logging.debug("\tOn a collection type of quest")
				quest_type = 'collect'
				clct = content['quests'][quest_key]['collect'].values()[0]
				quest_max = clct['count']
			# else if it's a boss, then hit up
			# content/quests/<quest_key>/boss/hp
			elif content.get('quests', {}).get(quest_key, {}).get('boss'):
				logging.debug("\tOn a boss/hp type of quest")
				quest_type = 'hp'
				quest_max = content['quests'][quest_key]['boss']['hp']

			# store repr of quest info from /content
			cache = update_quest_cache(CACHE_CONF,
									   quest_key=str(quest_key),
									   quest_type=str(quest_type),
									   quest_max=str(quest_max),
									   quest_title=str(quest_title))

		# now we use /party and quest_type to figure out our progress!
		quest_type = cache.get(SECTION_CACHE_QUEST, 'quest_type')
		if quest_type == 'collect':
			qp_tmp = party['quest']['progress']['collect']
			quest_progress = qp_tmp.values()[0]['count']
		else:
			quest_progress = party['quest']['progress']['hp']

		quest = '%s/%s "%s"' % (
				str(int(quest_progress)),
				cache.get(SECTION_CACHE_QUEST, 'quest_max'),
				cache.get(SECTION_CACHE_QUEST, 'quest_title'))

	# prepare and print status strings
	title = 'Level %d %s' % (stats['lvl'], stats['class'].capitalize())
	health = '%d/%d' % (stats['hp'], stats['maxHealth'])
	xp = '%d/%d' % (int(stats['exp']), stats['toNextLevel'])
	mana = '%d/%d' % (int(stats['mp']), stats['maxMP'])
	currentPet = items.get('currentPet', '')
	pet = '%s (%d food items)' % (currentPet, food_count)
	mount = items.get('currentMount', '')
	summary_items = ('health', 'xp', 'mana', 'quest', 'pet', 'mount')
	len_ljust = max(map(len, summary_items)) + 1
	print('-' * len(title))
	print(title)
	print('-' * len(title))
	print('%s %s' % ('Health:'.rjust(len_ljust, ' '), health))
	print('%s %s' % ('XP:'.rjust(len_ljust, ' '), xp))
	print('%s %s' % ('Mana:'.rjust(len_ljust, ' '), mana))
	print('%s %s' % ('Pet:'.rjust(len_ljust, ' '), pet))
	print('%s %s' % ('Mount:'.rjust(len_ljust, ' '), mount))
	print('%s %s' % ('Quest:'.rjust(len_ljust, ' '), quest))

    # GET/POST habits
def habit():
	habits = hbt.user.tasks(type='habits')
	if 'up' in args['<args>']:
		tids = get_task_ids(args['<args>'][1:])
		for tid in tids:
			tval = habits[tid]['value']
			hbt.user.tasks(_id=habits[tid]['id'],
						   _direction='up', _method='post')
			print('incremented task \'%s\''
				  % habits[tid]['text'].encode('utf8'))
			habits[tid]['value'] = tval + (TASK_VALUE_BASE ** tval)
			sleep(HABITICA_REQUEST_WAIT_TIME)
	elif 'down' in args['<args>']:
		tids = get_task_ids(args['<args>'][1:])
		for tid in tids:
			tval = habits[tid]['value']
			hbt.user.tasks(_id=habits[tid]['id'],
						   _direction='down', _method='post')
			print('decremented task \'%s\''
				  % habits[tid]['text'].encode('utf8'))
			habits[tid]['value'] = tval - (TASK_VALUE_BASE ** tval)
			sleep(HABITICA_REQUEST_WAIT_TIME)
	for i, task in enumerate(habits):
		score = qualitative_task_score_from_value(task['value'])
		print('[%s] %s %s' % (score, i + 1, task['text'].encode('utf8')))

    # GET/PUT tasks:daily
def daily(): 
	dailies = hbt.user.tasks(type='dailys')
	if 'done' in args['<args>']:
		tids = get_task_ids(args['<args>'][1:])
		for tid in tids:
			hbt.user.tasks(_id=dailies[tid]['id'],
						   _direction='up', _method='post')
			print('marked daily \'%s\' completed'
				  % dailies[tid]['text'].encode('utf8'))
			dailies[tid]['completed'] = True
			sleep(HABITICA_REQUEST_WAIT_TIME)
	elif 'undo' in args['<args>']:
		tids = get_task_ids(args['<args>'][1:])
		for tid in tids:
			hbt.user.tasks(_id=dailies[tid]['id'],
						   _method='put', completed=False)
			print('marked daily \'%s\' incomplete'
				  % dailies[tid]['text'].encode('utf8'))
			dailies[tid]['completed'] = False
			sleep(HABITICA_REQUEST_WAIT_TIME)
	print_task_list(dailies)

    # GET tasks:todo
def todo():
	todos = [e for e in hbt.user.tasks(type='todos')
			 if not e['completed']]
	if 'done' in args['<args>']:
		tids = get_task_ids(args['<args>'][1:])
		for tid in tids:
			hbt.user.tasks(_id=todos[tid]['id'],
						   _direction='up', _method='post')
			print('marked todo \'%s\' complete'
				  % todos[tid]['text'].encode('utf8'))
			sleep(HABITICA_REQUEST_WAIT_TIME)
		todos = updated_task_list(todos, tids)
	elif 'add' in args['<args>']:
		ttext = ' '.join(args['<args>'][1:])
		hbt.user.tasks(type='todo',
					   text=ttext,
					   priority=PRIORITY[args['--difficulty']],
					   _method='post')
		todos.insert(0, {'completed': False, 'text': ttext})
		print('added new todo \'%s\'' % ttext.encode('utf8'))
	print_task_list(todos)