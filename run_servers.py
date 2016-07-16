#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Start Pymol and Bokeh server """

from __future__ import print_function

import time
import shlex
import subprocess

__author__ = "Jérôme Eberhardt, Roland H Stote, and Annick Dejaegere"
__copyright__ = "Copyright 2016, Jérôme Eberhardt"
__credits__ = ["Jérôme Eberhardt", "Roland H Stote", "Annick Dejaegere"]

__lience__ = "MIT"
__maintainer__ = "Jérôme Eberhardt"
__email__ = "qksoneo@gmail.com"

def execute_command(cmd_line):
    args = shlex.split(cmd_line)
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = p.communicate()

    return output, errors

def start_screen_command(cmd, session_name):
    cmd_line = 'screen -d -m -S %s %s' % (session_name, cmd)
    return execute_command(cmd_line)

def stop_screen_command(session_name):
    cmd_line = 'screen -S %s -X quit' % session_name
    return execute_command(cmd_line)

def main():

    try:
        #Start Bokeh server and PyMOL
        start_screen_command('bokeh serve', 'visu_bokeh')
        start_screen_command('pymol -R', 'visu_pymol')

        while True:
            time.sleep(3600)

    except KeyboardInterrupt:
        pass

    finally:
        # Kill all screen session
        stop_screen_command('visu_bokeh')
        stop_screen_command('visu_pymol')

if __name__ == '__main__':
    main()