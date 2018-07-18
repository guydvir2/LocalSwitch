import sys
import getopt
from time import sleep
import os
from sys import path


def mqtt_commands(msg):
    if msg.upper() == 'UP':
        loc_double_switch.switch.switch0.switch_state = 1
    elif msg.upper() == 'STOP':
        loc_double_switch.switch.switch0.switch_state = 0
        loc_double_switch.switch.switch1.switch_state = 0
    elif msg.upper() == 'DOWN':
        loc_double_switch.switch.switch1.switch_state = 1
    elif msg.upper() == 'STATUS':
        print(loc_double_switch.switch.switch0.switch_state)
        print(loc_double_switch.switch.switch1.switch_state)
        print("info")
    else:
        print('Unrecognized command')


################## Path Parameters ##################
base_path = '/home/guy/github'
main_path = base_path + '/LocalSwitch'
sub_path = '/FamilyRoomWindow'
mod_path = base_path + '/RemoteSwitch'
path.append(mod_path)
path.append(main_path)
homedir = main_path + sub_path
from localswitches import HomePiLocalSwitch
from mqtt_switch import MQTTClient
import getip

######################################################

################## Switch Parameters #################
device_name = 'F-RoomWindow'
switch_type = 'double'
gpio_in = [20, 21]
gpio_out = [19, 26]
mode = 'press'
ext_log = homedir + '/%s.log' % device_name
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


####################  MQTT parameters  #################
# mqtt_host='192.168.2.113' #internal
mqtt_host = 'iot.eclipse.org'  # external
heir_topic = '/HomePi/Dvir/Windows/'
device_topic = heir_topic + device_name

#######################################################
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
                                 body='Device loaded successfully @%s' % getip.get_ip()[0])

# Run MQTT protocol
mqtt_agent = MQTTClient(sid=device_name, topic=device_topic, topic_qos=0, host=mqtt_host)
mqtt_agent.call_externalf = lambda: mqtt_commands(mqtt_agent.arrived_msg)
mqtt_agent.start()

# Boot test
if switch_type == 'double':
    loc_double_switch.switch.switch0.switch_state = 1
    sleep(0.5)
    loc_double_switch.switch.switch0.switch_state = 0
    sleep(0.5)
    loc_double_switch.switch.switch1.switch_state = 1
    sleep(0.5)
    loc_double_switch.switch.switch1.switch_state = 0
