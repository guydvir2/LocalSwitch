import sys
import getopt
from time import sleep
import os
from sys import path
import datetime
import sys


def start_switch_code():
    global loc_double_switch
    loc_double_switch = HomePiLocalSwitch(switch_type=switch_type,
                                          gpio_in=gpio_in, gpio_out=gpio_out, mode=mode,
                                          ext_log=ext_log, alias=device_name, sw0_name=sw0_name,
                                          sw1_name=sw1_name)


def PBit():
    if switch_type == 'double':
        loc_double_switch.switch.switch0.switch_state = 1
        sleep(0.5)
        loc_double_switch.switch.switch0.switch_state = 0
        sleep(0.5)
        loc_double_switch.switch.switch1.switch_state = 1
        sleep(0.5)
        loc_double_switch.switch.switch1.switch_state = 0


def read_conf_file(confile):
    global file_param
    if os.path.isfile(confile) is True:
        with open(confile, 'r') as f:
            data_file = f.readlines()
            for line in data_file:
                # skip empty line in conf file or commented line
                if line.strip() != '':
                    file_param[line.split('=')[0].strip()] = line.split('=')[1].split('\n')[0].strip()
    else:
        print('file', confile, ' not found')
        quit()


def confile_path_cmdline():
    global confloc
    argv = sys.argv[1:]
    if len(argv) > 0:
        confloc = argv[0]


def start_gmail():
    ## Run Gmail defs
    global s_file, p_file
    recps = ['guydvir.tech@gmail.com']
    loc_double_switch.gmail_defs(recipients=recps, sender_file=s_file,
                                 password_file=p_file)


def start_schedule():
    if file_param["ENABLE_SCHED"] == 'True':
        loc_double_switch.weekly_schedule(local_schedule_0=local_schedule_0,
                                          sched_filename_0=sched_filename_0, local_schedule_1=local_schedule_1,
                                          sched_filename_1=sched_filename_1)


def start_mqtt_service():
    global mqtt_agent
    topics = [device_topic, group_topic]
    mqtt_agent = MQTTClient(sid=device_name, topics=topics, topic_qos=0, host=mqtt_host)
    mqtt_agent.call_externalf = lambda: mqtt_commands(mqtt_agent.arrived_msg)
    mqtt_agent.start()


def mqtt_commands(msg):
    if msg.upper() == 'UP':
        loc_double_switch.switch.switch0.switch_state = 1
        pub_msg('CMD [UP]')
    elif msg.upper() == 'OFF':
        loc_double_switch.switch.switch0.switch_state = 0
        loc_double_switch.switch.switch1.switch_state = 0
        pub_msg('CMD [OFF]')

    elif msg.upper() == 'DOWN':
        loc_double_switch.switch.switch1.switch_state = 1
        pub_msg('CMD [DOWN]')

    elif msg.upper() == 'STATUS':

        state_0 = "[%s] Relay state: %d, Switch state: %d" % (
            sw0_name, loc_double_switch.switch.switch0.switch_state[0],
            loc_double_switch.switch.switch0.switch_state[1])

        state_1 = "[%s] Relay state: %d, Switch state: %d" % (
            sw1_name, loc_double_switch.switch.switch1.switch_state[0],
            loc_double_switch.switch.switch1.switch_state[1])

        pub_msg(state_0 + '; ' + state_1)
    else:
        pass


def pub_msg(msg):
    time_stamp = '[' + str(datetime.datetime.now())[:-5] + ']'
    mqtt_agent.pub(payload='%s [%s] %s' % (time_stamp, device_name, msg), topic=msg_topic)


################## Path Parameters ##################
file_param = {}
# confloc = '/home/guy/github/LocalSwitch/rooms/ParentsRoomWindow/'
confile_path_cmdline()
confile_name = 'HomePi_SW.conf'
read_conf_file(confloc + confile_name)
base_path = file_param["BASE_PATH"]
main_path = file_param["MAIN_PATH"]
mod_path = file_param["MOD_PATH"]
homedir = confloc
path.append(mod_path)
path.append(main_path)

from localswitches import HomePiLocalSwitch
from mqtt_switch import MQTTClient
import getip

######################################################

################## Switch Parameters #################
device_name = file_param["DEVICE_NAME"]
gpio_in = [int(file_param["GPIO_IN"].split(',')[0]), int(file_param["GPIO_IN"].split(',')[1])]
gpio_out = [int(file_param["GPIO_OUT"].split(',')[0]), int(file_param["GPIO_OUT"].split(',')[1])]
ext_log = homedir + '%s.log' % device_name
s_file = main_path + 'ufile.txt'
p_file = main_path + 'pfile.txt'
sw0_name = '/Up'
sw1_name = '/Down'
mode = 'press'
switch_type = 'double'
#######################################################

########################  Schedule 0  #################
# Select One
local_schedule_0 = None
sched_filename_0 = homedir + file_param["SCHED_UP"]
#######################################################

########################  Schedule 1  #################
# Select One
# DoubleSwitch only
local_schedule_1 = None
sched_filename_1 = homedir + file_param["SCHED_DOWN"]
#######################################################

########################  Schedule examples ###########
# {'start_days': [3], 'start_time': '19:03:00', 'end_days': [4], 'end_time': '23:08:00'}
# sched_filename_1='/home/guy/Documents/github/Rpi/modules/sched1.txt')
#######################################################


####################  MQTT parameters  #################
mqtt_host = '192.168.2.113'  # internal
# mqtt_host = 'iot.eclipse.org'  # external
main_topic = file_param["MAIN_TOPIC"]
group_topic = file_param["GROUP_TOPIC"]
msg_topic = file_param["MSG_TOPIC"]
device_topic = file_param["DEVICE_TOPIC"]
#######################################################


# Run Switch
start_switch_code()

# Run Watch_dog service
loc_double_switch.use_watch_dog()

# Run Local schedule
start_schedule()

## Run Gmail service
start_gmail()

## Notify after boot
loc_double_switch.notify_by_mail(subj='HomePi:%s boot summery' % device_name,body='Device loaded successfully @%s' % getip.get_ip()[0])

# Run MQTT service
start_mqtt_service()
sleep(1)
pub_msg('System Boot')

# Boot test
PBit()
