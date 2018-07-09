import sys
import getopt
from time import sleep
import os
from sys import path

################## Path Parameters ##################
main_path = '/home/guy/github/LocalSwitch'
sub_path='/Salon2Window'
path.append(main_path)
homedir = main_path + sub_path
from localswitches import HomePiLocalSwitch
import getip
######################################################

################## Switch Parameters #################
device_name = 'S2-Window'
switch_type = 'double'
gpio_in = [20, 21]
gpio_out = [19, 26]
mode = 'press'
ext_log = homedir + '/%s.log' % (device_name)
recps = ['guydvir.tech@gmail.com']
s_file = main_path + '/ufile.txt'
p_file = main_path + '/pfile.txt'
sw0_name = '/Up'
sw1_name = '/Down'
#######################################################

########################  Schedule 0  #################
# Select One
local_schedule_0 = None
sched_filename_0 = homedir + '/sched_up.txt'
#######################################################


########################  Schedule 1  #################
# Select One
# DoubleSwitch only
local_schedule_1 = None
sched_filename_1 = homedir + '/sched_down.txt'
#######################################################


########################  Schedule examples ###########
# {'start_days': [3], 'start_time': '19:03:00', 'end_days': [4], 'end_time': '23:08:00'}
# sched_filename_1='/home/guy/Documents/github/Rpi/modules/sched1.txt')
#######################################################


argv = sys.argv[1:]

if len(argv) > 0:
    try:
        opts, args = getopt.getopt(argv, "u:d:s", ["up=", "down=", "status="])
    except getopt.GetoptError:
        print('-u<state> -d<state>')
        sys.exit(2)

    a = HomePiLocalSwitch(switch_type='double', gpio_in=[20, 21], 
            gpio_out=[16, 26], mode='press', 
            ext_log='/home/guy/Documents/%s.log' % (device_name), 
            alias=device_name + 'O/D')

    switch = ''
    for opt, arg in opts:
        if opt == '-h':
            print('-u --up -d --down, state=<on/off>')
            sys.exit(2)
        elif opt in ("-u", "--up"):
            switch = arg
            if arg == 'on':
                a.switch.switch0.switch_state = 1
            elif arg == "off":
                a.switch.switch0.switch_state = 0
        elif opt in ("-d", "--down"):
            switch = arg
            if arg == 'on':
                a.switch.switch0.switch_state = 1
            elif arg == "off":
                a.switch.switch1.switch_state = 0
        elif opt in ("-s", "--status"):
            print(a.switch.switch0.switch_state)



else:
    # Run Switch
    loc_double_switch = HomePiLocalSwitch(switch_type=switch_type, 
            gpio_in=gpio_in, gpio_out=gpio_out, mode=mode, 
            ext_log=ext_log, alias=device_name, sw0_name=sw0_name, 
            sw1_name=sw1_name)

    # Run Watch_dog service
    loc_double_switch.use_watch_dog()

    # Run Local schedule
    loc_double_switch.weekly_schedule(local_schedule_0=local_schedule_0, 
            sched_filename_0=sched_filename_0, local_schedule_1=local_schedule_1, 
            sched_filename_1=sched_filename_1)

    # Run Gmail defs
    loc_double_switch.gmail_defs(recipients=recps, sender_file=s_file, 
            password_file=p_file)

    # Notify after boot
    loc_double_switch.notify_by_mail(subj='HomePi:%s boot summery' % device_name, 
            body='Device loaded successfully @%s'%getip.get_ip()[0])

    # Boot test
    if switch_type == 'double':
        loc_double_switch.switch.switch0.switch_state = 1
        sleep(0.5)
        loc_double_switch.switch.switch0.switch_state = 0
        sleep(0.5)
        loc_double_switch.switch.switch1.switch_state = 1
        sleep(0.5)
        loc_double_switch.switch.switch1.switch_state = 0
