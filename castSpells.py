#!/usr/bin/env python
from habitica import api 
import requests
import json
from hab_task import HabTask
import os
import main
import manaPull

auth, hbt = main.get_started('auth.cfg')

manaPull.cast_all_mana(auth,'valorousPresence')
