#!/usr/bin/env python

"""
Here are things you'll need to install before it runs...
"""

pip install pytodoist
pip install scriptabit
"""
We can't directly install the main habitica pip because the API is broken. Until philadams 
gets around to to accepting the pull request, we'll need to install a workaround from synacktic...
"""
git clone https://github.com/synacktic/habitica
pip install -e habitica
