from sys import path
import datetime
from time import sleep
import os
import sys

mod_path='/home/guy/github/modules/'
main_path='/home/guy/github/RemoteSwitch'
path.append(mod_path)
path.append(main_path)

import scheduler
from mqtt_switch import MQTTClient


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



def start_mqtt_service():
    global mqtt_agent, MQTT_HOST, DEVICE_NAME, DEVICE_TOPIC, MSG_TOPIC, SCH_TOPIC
    
    topics = [SCH_TOPIC, GROUP_TOPIC]
    mqtt_agent = MQTTClient(sid=DEVICE_NAME, topics=topics, topic_qos=0, host=MQTT_HOST)
    mqtt_agent.call_externalf = lambda: mqtt_commands(mqtt_agent.arrived_msg)
    mqtt_agent.start()
    sleep(1)
    pub_msg(msg_topic=MSG_TOPIC,msg='Schedule is UP')

def mqtt_commands(msg):
    if msg.upper() == 'UP':
        pub_msg('up')
    elif msg.upper() == 'OFF':
        pub_msg('off')
    elif msg.upper() == 'DOWN':
        pub_msg('down')
    elif msg.upper() == 'STATUS':
        pub_msg(state_0 + '; ' + state_1)
    else:
        pass

def pub_msg(msg,msg_topic=None):
    global MSG_TOPIC, DEVICE_TOPIC
    if msg_topic == None:
        msg_topic = DEVICE_TOPIC
    else:
        msg_topic = MSG_TOPIC
    mqtt_agent.pub(payload=msg, topic=msg_topic)

def conv_list_int(list1):
    a=list1.split(',')
    aa=[int(i) for i in a]
    return aa
    
def up_schedule():
    global UP_START_DAYS,UP_END_DAYS,UP_START_TIME, UP_END_TIME
    schedule_up = scheduler.RunWeeklySchedule(on_func=sched_on_func, off_func=sched_off_func)
    schedule_up.add_weekly_task(new_task={'start_days': UP_START_DAYS, 'start_time': UP_START_TIME,
     'end_days': UP_END_DAYS, 'end_time': UP_END_TIME})
    schedule_up.start()
    
def down_schedule():
    global DOWN_START_DAYS,DOWN_END_DAYS,DOWN_START_TIME, DOWN_END_TIME
    schedule_down = scheduler.RunWeeklySchedule(on_func=sched_down_func, off_func=sched_off_func)
    schedule_down.add_weekly_task(new_task={'start_days': DOWN_START_DAYS, 'start_time': DOWN_START_TIME,
    'end_days': DOWN_END_DAYS, 'end_time': DOWN_END_TIME})
    schedule_down.start()

def sched_on_func():
    #pub_msg("up")
    print("up")
    
def sched_off_func():
    #pub_msg("off")
    print("off")
    
def sched_down_func(): 
    #pub_msg("down")
    print("down")
 
 
################## Config file Parameters ########## 
file_param={}       
confloc = '/home/guy/github/LocalSwitch/rooms/FamilyRoomWindow/'                  
confile_path_cmdline()
confile_name = 'HomePi_SCH.conf'
read_conf_file(confloc + confile_name)                                                                                              
DEVICE_NAME = file_param['DEVICE_NAME']
MQTT_HOST = '192.168.2.113'
# To send msg to All
MSG_TOPIC = file_param['MSG_TOPIC'] 
# To communicate with this MQTT regrading SCH
SCH_TOPIC = file_param['SCH_TOPIC'] 
# Send SCH operation to HW 
DEVICE_TOPIC = file_param['DEVICE_TOPIC'] 
GROUP_TOPIC = file_param['GROUP_TOPIC'] 
UP_START_DAYS = conv_list_int(file_param['up_start_days'])
UP_START_TIME = file_param['up_start_time']
UP_END_DAYS = conv_list_int(file_param['up_end_days'])
UP_END_TIME = file_param['up_end_time']
DOWN_START_DAYS = conv_list_int(file_param['down_start_days'])
DOWN_START_TIME = file_param['down_start_time']
DOWN_END_DAYS = conv_list_int(file_param['down_end_days'])
DOWN_END_TIME = file_param['down_end_time']

####################################################

####### Start Here ########
start_mqtt_service()
up_schedule()
down_schedule()



