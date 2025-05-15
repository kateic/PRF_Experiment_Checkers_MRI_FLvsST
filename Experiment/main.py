#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 14:04:44 2019

@author: marcoaqil

forked: kathie 2020/1

"""
import sys
import os
from session import PRFSession
from datetime import datetime
datetime.now().strftime('%Y-%m-%d %H:%M:%S')


# ####### for testing ##########
# os.chdir('/Users/kathie/Documents/code/PRF_code/PRF_Experiment_Checkers-fork_MRI-FLvsST/Experiment')

# subject = 'sub-001'
# sess    = 'ses-1'
# task    = 'task-FL10hz'
# run     = 'run-1'
# #################################

def main():
    subject = sys.argv[1]
    sess    = sys.argv[2]
    task    = sys.argv[3] #either task-FL10hz or task-ST
    run     = sys.argv[4]
    
    
    output_str = subject+'_'+sess+'_'+task+'_'+run
    
    output_dir = './'+output_str+'_Logs'
    
    if os.path.exists(output_dir):
        print("Warning: output directory already exists. Renaming to avoid overwriting.")
        output_dir = output_dir + datetime.now().strftime('%Y%m%d%H%M%S')
    
    settings_file = './expsettings_'+task[5:]+'.yml'

    ts = PRFSession(output_str=output_str, output_dir=output_dir, settings_file=settings_file)
    ts.run()

if __name__ == '__main__':
    main()