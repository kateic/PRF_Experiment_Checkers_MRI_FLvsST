# PRF_Experiment
Repository for PRF mapping experiment stimulus

Requirements: psychopy and exptools2

**Usage**

Create setting files named expsettings_*Task*.yml within the Experiment folder. Change *Task* to your actual task name. Run the following line from within the Experient folder.

- python main.py sub-*xxx* ses-*x* task-*NameTask* run-*x*

Subject SHOULD be specified according the the BIDS convention (sub-001, sub-002 and so on), Task MUST match one of the settings files in the Experiment folder, and Run SHOULD be an integer.



**Flickering vs standard pRF stimulus**

This code is an updated version of standard PRF stimulus with checkers from [marcoaqil's version](https://github.com/marcoaqil/PRF_Experiment_Checkers).
It presents either a flickering checkerboard or the standard moving checkerboard within the bar apertures, by calling two different settings files that are located in the Experiment folder. The task names are:
- FL10hz : flickering checkerboard at a flipping rate of 10Hz (square wave frequency of 5Hz)
- ST :  standard moving pRF stimulus with 2 squares at regular speed

Both versions have the standard fixation dot color discrimination task.

Both versions allow to change the stimulus size depending on a second monitor setup.
This was done to accommodate for later experiments that include an MRI and MEG session that presents the stimulus at the same degrees of visual angle.
This can be turned off by setting the Single monitor mode to True in the settings file.



**Settings file**

The *task parameters* can be changed in the settings file under "Task settings:"
- It can be specified how much time the participant have to respond that still counts as correct response (default is 0.8s), as "response interval: *your time*"
- The timing of the color switches can be specified (default is 3.5s), as "color switch interval: *your interval*"
Note: Make sure that the difference between two adjacent color switches is bigger than the time you give the participant to respond.
The code adds a randomization of max. +1 or -1 to the color switch times, so e.g. in case of a color switch interval of 3.5, the two closest adjacent color switches will be 1.5s apart, well outside the response interval of 0.8s.

Different flicker frequencies can be implemented by creating a new settingsfile, changing the frequency parameter.
Note: keep in mind that specifying a frequency of 10 Hz creates a stimulus that flips the checkerboard at 10Hz. The actual square wave is thus 5Hz.
