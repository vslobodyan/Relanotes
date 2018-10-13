# -*- coding: utf-8 -*-
#!/usr/bin/python3


import sys
# import logging
# import os

# Check if we run the correct python version
try:
    version_info = sys.version_info
    assert version_info > (3, 0)
except:
    print >> sys.stderr, 'ERROR: Relanotes needs python > 3.0)'
    sys.exit(1)


# Try importing our modules

# Попытка импортировать модуль с PyQT5

# ...


try:
    import relanotes.main
except ImportError:
    sys.excepthook(*sys.exc_info())
    print >> sys.stderr, 'ERROR: Could not find python module files in path:'
    print >> sys.stderr, ' '.join(map(str, sys.path))
    print >> sys.stderr, '\nTry setting PYTHONPATH'
    sys.exit(1)


