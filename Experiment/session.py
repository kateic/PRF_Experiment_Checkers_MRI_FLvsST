#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 14:05:10 2019

@author: marcoaqil

forked: kathie 2020/1

"""

import numpy as np
import os
from psychopy import visual
from psychopy.visual import filters
from psychopy import tools
from psychopy.monitors import Monitor 

from exptools2.core.session import Session
from trial import PRFTrial
from stim import PRFStim

opj = os.path.join


class PRFSession(Session):

    
    def __init__(self, output_str, output_dir, settings_file):
        
        
        super().__init__(output_str=output_str, output_dir=output_dir, settings_file=settings_file)
        
        #if we are scanning, here I set the mri_trigger manually to the 't'. together with the change in trial.py, this ensures syncing
        if self.settings['mri']['topup_scan']==True:
            self.topup_scan_duration=self.settings['mri']['topup_duration']
        
        if self.settings['PRF stimulus settings']['Scanner sync']==True:
            self.bar_step_length = self.settings['mri']['TR']
            self.mri_trigger='t'

                     
        else:
            self.bar_step_length = self.settings['PRF stimulus settings']['Bar step length']
            
        if self.settings['PRF stimulus settings']['Screenshot']==True:
            self.screen_dir=output_dir+'/'+output_str+'_Screenshots'
            if not os.path.exists(self.screen_dir):
                os.mkdir(self.screen_dir)
            
        
        #determine whether need to adjust the stimulus size 
        if self.settings['Single monitor'] == False: #stim size depends on both MEG and MRI screen
            # get MEG screen specs information 
            MEGmonitor = Monitor(**self.settings['MEG']['monitor'])
            MEGmonitor.setSizePix(self.settings['MEG']['window']['size'])
            
            #get size in visual degree along vertical axis 
            self.MEGwin_in_deg = tools.monitorunittools.pix2deg( self.settings['MEG']['window']['size'][1], MEGmonitor)
            self.MRIwin_in_deg = tools.monitorunittools.pix2deg( self.win.size[1] , self.monitor)
            
            #set stimulus size (dependent on which is smaller screen) 
            self.stim_size = np.min([self.MEGwin_in_deg, self.MRIwin_in_deg])
            #determine stimulus size in pixels on current screen 
            self.stim_size_in_pix = int(tools.monitorunittools.deg2pix(self.stim_size, self.monitor))
            
            
        else: #stim size only depends on MRI screen size 
            self.stim_size_in_pix = self.settings['window']['size'][1]
        
            
        
        #create all stimuli and trials at the beginning of the experiment, to save time and resources        
        self.create_stimuli()
        self.create_trials()
            
        





    def create_stimuli(self):
        
        
        #generate PRF stimulus
        self.prf_stim = PRFStim(session   = self, 
                        squares_in_bar    = self.settings['PRF stimulus settings']['Squares in bar'], 
                        bar_width_deg     = self.settings['PRF stimulus settings']['Bar width in degrees'],
                        flicker_frequency = self.settings['PRF stimulus settings']['Checkers motion speed'])#self.deg2pix(self.settings['prf_max_eccentricity']))    
        

        #currently unused
        #self.instruction_string = """Please fixate in the center of the screen. Your task is to respond whenever the dot changes color."""
        
        #raised cosine alpha mask depending on stimulus size
        mask = filters.makeMask(matrixSize  = self.win.size[0], 
                                shape       = 'raisedCosine',
                                radius      = np.array([self.stim_size_in_pix/self.win.size[0], self.stim_size_in_pix/self.win.size[1]]), 
                                center      = (0.0, 0.0), 
                                range       = [-1, 1], 
                                fringeWidth = 0.02
                                )

        self.mask_stim = visual.GratingStim(self.win, 
                                        mask    = -mask, 
                                        tex     = None, 
                                        units   = 'pix',
                                        size    = [self.win.size[0],self.win.size[1]], 
                                        pos     = np.array((0.0,0.0)), 
                                        color   = [0,0,0])   
                                        



        #as basic task, generate fixation circles of different colors, with black border
        fixation_radius_pixels=tools.monitorunittools.deg2pix(self.settings['PRF stimulus settings']['Size fixation dot in degrees'], self.monitor)/2
            
        #two colors of the fixation circle for the task
        self.fixation_disk_0 = visual.Circle(self.win, 
            units='pix', radius=fixation_radius_pixels, 
            fillColor=[1,-1,-1], lineColor=[1,-1,-1])
        
        self.fixation_disk_1 = visual.Circle(self.win, 
            units='pix', radius=fixation_radius_pixels, 
            fillColor=[-1,1,-1], lineColor=[-1,1,-1])




    def create_trials(self):
        """creates trials by setting up prf stimulus sequence"""
        
        self.trial_list = []
        
        #simple tools to check subject responses online
        self.correct_responses = 0
        self.total_responses = 0
        self.dot_count = 0 
        
        
        bar_orientations = np.array(self.settings['PRF stimulus settings']['Bar orientations'])
        
        
        #create as many trials as TRs. 5 extra TRs at beginning + bar passes + blanks
        self.trial_number = 5 + self.settings['PRF stimulus settings']['Bar pass steps'] * \
                                    len(np.where(bar_orientations != -1)[0]) + \
                                self.settings['PRF stimulus settings']['Blanks length'] * \
                                    len(np.where(bar_orientations == -1)[0])
        print("Expected number of TRs: %d"%self.trial_number)
        
        
        
        #create bar orientation list for each TR 
        steps_array  = self.settings['PRF stimulus settings']['Bar pass steps'] * np.ones(len(bar_orientations))
        blanks_array = self.settings['PRF stimulus settings']['Blanks length'] * np.ones(len(bar_orientations))
    
        repeat_times = np.where(bar_orientations == -1, blanks_array, steps_array).astype(int)
 
        self.bar_orientation_at_TR = np.concatenate((-1*np.ones(5), np.repeat(bar_orientations, repeat_times)))
        
        
        
        #create bar position list for each TR 
        #bar positions depend on total stim size 
        bar_pos_array = self.stim_size_in_pix * np.linspace(-0.5,0.5, self.settings['PRF stimulus settings']['Bar pass steps'])
        
        blank_array = np.zeros(self.settings['PRF stimulus settings']['Blanks length'])
        
        #the 5 empty trials at beginning
        self.bar_pos_in_ori = np.zeros(5)
        
        #bar positions at TR (position = 0 for blanks )
        for i in range(len(bar_orientations)):
            if bar_orientations[i] == -1:
                self.bar_pos_in_ori = np.append(self.bar_pos_in_ori, blank_array)
            else:
                self.bar_pos_in_ori = np.append(self.bar_pos_in_ori, bar_pos_array)
                   
     
        
        #random bar direction at each step, only for standard moving stimulus 
        self.bar_direction_at_TR = np.round(np.random.rand(self.trial_number))
        
        
        
        #trial list
        for i in range(self.trial_number):
                
            self.trial_list.append(PRFTrial(
                            session             = self,
                            trial_nr            = i,                 
                            bar_orientation     = self.bar_orientation_at_TR[i],
                            bar_position_in_ori = self.bar_pos_in_ori[i],
                            bar_direction       = self.bar_direction_at_TR[i]
                            #,tracker           = self.tracker
                            ))



        #times for dot color change and continue the task into the topup
        self.total_time = self.trial_number * self.bar_step_length 
        
        if self.settings['mri']['topup_scan'] == True:
            self.total_time += self.topup_scan_duration
        
        
        #dot color change times
        self.dot_switch_color_times = np.arange(3, self.total_time, float(self.settings['Task settings']['color switch interval']))
        self.dot_switch_color_times += (2*np.random.rand(len(self.dot_switch_color_times))-1)
        
        
        #keep track of which dot to print
        self.current_dot_time = 0
        self.next_dot_time    = 1


        np.save(opj(self.output_dir, self.output_str+'_DotSwitchColorTimes.npy'), self.dot_switch_color_times)
        print(self.win.size)




    def draw_stimulus(self):
        #this timing is used for the motion of checkerboards inside the bar. it does not have any effect on the actual bar motion
        present_time = self.clock.getTime()
               
  
        #draw the bar at the required orientation for this TR, unless the orientation is -1, code for a blank period
        if self.current_trial.bar_orientation != -1:
            self.prf_stim.draw(time          = present_time, 
                               pos_in_ori    = self.current_trial.bar_position_in_ori, 
                               orientation   = self.current_trial.bar_orientation,
                               bar_direction = self.current_trial.bar_direction)
            
            
        #draw the correct dot color
        if self.next_dot_time < len(self.dot_switch_color_times):
            if present_time < self.dot_switch_color_times[self.current_dot_time]:                
                self.fixation_disk_1.draw()
            else:
                if present_time < self.dot_switch_color_times[self.next_dot_time]:
                    self.fixation_disk_0.draw()
                else:
                    self.current_dot_time += 2
                    self.next_dot_time += 2
                    



    def run(self):
        """run the session"""
        
        self.display_text('Waiting for scanner', keys=self.settings['mri'].get('sync', 't'))

        #start timing and bookkeeping
        self.start_experiment()
        
        #cycle through trials
        for trial_idx in range(len(self.trial_list)):
            self.current_trial = self.trial_list[trial_idx]
            self.current_trial_start_time = self.clock.getTime()
            self.current_trial.run()
        
        
        print(f"Expected number of responses: {len(self.dot_switch_color_times)}")
        print(f"Total subject responses: {self.total_responses}")
        print(f"Correct responses (within {self.settings['Task settings']['response interval']}s of dot color change): {self.correct_responses}")
        np.save(opj(self.output_dir, self.output_str+'_simple_response_data.npy'), {"Expected number of responses":len(self.dot_switch_color_times),
        														                      "Total subject responses":self.total_responses,
        														                      f"Correct responses (within {self.settings['Task settings']['response interval']}s of dot color change)":self.correct_responses})
        
        print('Percentage of correctly answered trials: %.2f%%'%(100*self.correct_responses/np.size(self.dot_switch_color_times)))
        
        
        if self.settings['PRF stimulus settings']['Screenshot'] == True:
            self.win.saveMovieFrames(opj(self.screen_dir, self.output_str+'_Screenshot.png'))
            
        self.close()

        

