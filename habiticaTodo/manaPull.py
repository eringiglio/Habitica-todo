#!/usr/bin/env python
import requests
import json
from hab_task import HabTask
import os
import main

try:
    import ConfigParser as configparser
except:
    import configparser	

classSkills = {
    "Mage" : {"Burst of Flames":"fireball","Ethereal Surge" : "mpHeal", "Earthquake":"earth", "Chilling Frost" : "frost"},
    "Warrior": {"Brutal Smash":"smash", "Defensive Stance" : "defensiveStance", "Valorous Presence" : "valorousPresence", "Intimidating Gaze" : "intimidate"},
    "Rogue" : {"Pickpocket" : "pickPocket", "Backstab" : "backStab", "Tools of the Trade": "toolsOfTrade", "Stealth" : "stealth"},
    "Healer" : {"Healing Light" : "heal", "Protective Aura" : "protectAura", "Searing Brightness" : "brightness", "Blessing" : "healAll"}}
skillCost = {"fireball": 10, "mpHeal": 30, "earth" : 35, "frost" : 40, "smash" : 10, "defensiveStance" : 25, "valorousPresence" : 20, "intimidate" : 15, "pickPocket" : 10, "backStab" : 15, "toolsOfTrade" : 25, "stealth" : 45, "heal" : 15, "protectAura" : 30, "brightness" : 15, "healAll" : 25}

def get_user_info(auth):
    import requests
    import json
    url = 'https://habitica.com/api/v3/user/'
    r = requests.get(headers=auth, url=url)
    user = r.json()
    userData = user['data']
    return userData

def get_user_mana(auth):
    from manaPull import get_user_info
    userData = get_user_info(auth)
    mana = userData['stats']['mp']
    return mana

def assgn_user_attr_pts(auth):
    '''
    This is totally a me thing: I like to assign my points in a ratio of 2 str, 1 int, 1 per. So I'm writing a routine that will automatically do that for me.
    '''
    from manaPull import get_user_info
    import json
    url = 'https://habitica.com/api/v3/user/allocate'
    userData = get_user_info(auth)
    stats = userData['stats']
    if stats['points'] <= 1:
        strength = stats['str']
        perception = stats['per']
        intelligence = stats['int']
        constitution = stats['con']
        total = strength + perception + intelligence + constitution + stats['points']
        if total % 2 == 0:
            data = json.dumps({"stat" : "str"})
        elif (total - 1) % 4 == 0: 
            data = json.dumps({"stat" : "int"})
        else: 
            data = json.dumps({"stat" : "per"})
        r = requests.post(headers=auth,url=url,data=data)
        return r


def cast_skill(auth, skill):
    import requests
    import json
    url = 'https://habitica.com/api/v3/user/class/cast/'
    url += str(skill)
    r = requests.post(headers=auth, url=url)
    return r

def cast_all_mana(auth, skill):
    from manaPull import get_user_mana
    from manaPull import skillCost
    from manaPull import cast_skill
    import requests
    import json
    import time
    
    mana = get_user_mana(auth)
    cost = skillCost[skill]
    num_casts = int(mana/cost)
    r_list = []
    
    for cast in range(1,num_casts+1):
        r = cast_skill(auth, skill)
        r_list.append(r)
        time.sleep(1.2)
    
    url = 'https://habitica.com/api/v3/tasks/buffHabit/score/up'
    r = requests.post(headers=auth,url=url)