# -*- coding: utf-8 -*-
""" Implements a Todoist synchronisation task.
"""
# Ensure backwards compatibility with Python 2
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals)
from builtins import *
from datetime import datetime
from tzlocal import get_localzone

from .dates import parse_date_utc
from .task import CharacterAttribute, ChecklistItem, Difficulty, Task

"""
So what if I did todoist work a sliiiightly different way, using all my task IDs?
"""