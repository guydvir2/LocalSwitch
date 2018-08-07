from sys import path
import datetime
from time import sleep
import os
import sys

mod_path = '/home/guy/github/modules/'
main_path = '/home/guy/github/RemoteSwitch'
path.append(mod_path)
path.append(main_path)

import scheduler
from mqtt_switch import MQTTClient


class MQTTRemoteSchedule:
    def __init__(self, master_topic, pub_topics, msg_topic, device_name, broker='192.168.2.113', qos=0, active=True):
        self.param_file, self.confile_loc = None, None
        self.def_sched_down_1, self.def_sched_down_2 = {}, {}
        self.def_sched_up_1, self.def_sched_up_2 = {}, {}
        self.pub_topics, self.msg_topic = [pub_topics, master_topic + '_SCHD'], msg_topic
        self.broker, self.master_topic = broker, master_topic
        self.active_schedule_flag = active
        self.boot_time = datetime.datetime.now()

        self.start_mqtt_service(device_name, qos)
        self.default_schedules()
        self.start_up_schedule()
        self.start_down_schedule()

    def start_mqtt_service(self, device_name, qos):
        self.mqtt_agent = MQTTClient(sid=device_name, topics=self.pub_topics, topic_qos=qos, host=self.broker)
        self.mqtt_agent.call_externalf = lambda: self.mqtt_commands(self.mqtt_agent.arrived_msg)
        self.mqtt_agent.start()
        sleep(1)

        self.pub_msg(msg_topic=self.msg_topic, msg='Schedule is UP')

    def mqtt_commands(self, msg):
        msg_codes = [0, 1, 2, 3, 4, 5, 6]
        msg_text = ['UP', 'DOWN', 'OFF', 'STATUS', 'DIS_SHCD', 'ENB_SCHD', 'REPORT']
        if msg.upper() == msg_text[0] or msg_codes[0]:
            self.pub_msg(msg_text[0].lower())
        elif msg.upper() == msg_text[1] or msg.upper() == msg_codes[1]:
            self.pub_msg(msg_text[1].lower())
        elif msg.upper() == msg_text[2] or msg.upper() == msg_codes[2]:
            self.pub_msg(msg_text[2].lower())
        elif msg.upper() == msg_text[3] or msg.upper() == msg_codes[3]:
            self.pub_msg(msg_text[3].lower())
        elif msg.upper() == msg_text[4] or msg.upper() == msg_codes[4]:
            self.pub_msg(msg_text[4].lower())
        elif msg.upper() == msg_text[5] or msg.upper() == msg_codes[5]:
            self.pub_msg(msg_text[5].lower())
        elif msg.upper() == msg_text[6] or msg.upper() == msg_codes[6]:
            a = self.schedule_up.tasks_descriptive()
            print(a)
            # self.pub_msg(msg_text[6].lower())
        else:
            pass

    def pub_msg(self, msg, msg_topic=None):
        if msg_topic == None:
            msg_topic = self.master_topic
        else:
            time_stamp = '[' + str(datetime.datetime.now())[:-5] + ']'
            msg = '%s [%s] %s' % (time_stamp, self.master_topic.split('/')[-1], msg)

        self.mqtt_agent.pub(payload=msg, topic=msg_topic)

    def start_up_schedule(self):
        self.schedule_up = scheduler.RunWeeklySchedule(on_func=lambda: self.pub_msg('up'),
                                                       off_func=lambda: self.pub_msg('off'))
        self.schedule_up.add_weekly_task(new_task=self.def_sched_up_1)
        self.schedule_up.add_weekly_task(new_task=self.def_sched_up_2)
        self.schedule_up.start()

    def start_down_schedule(self):
        self.schedule_down = scheduler.RunWeeklySchedule(on_func=lambda: self.pub_msg('down'),
                                                         off_func=lambda: self.pub_msg('off'))
        self.schedule_down.add_weekly_task(new_task=self.def_sched_down_1)
        self.schedule_down.add_weekly_task(new_task=self.def_sched_down_2)
        self.schedule_down.start()

    def default_schedules(self):
        self.def_sched_up_1 = {'start_days': [1, 2, 3, 4, 5], 'start_time': '06:30:00',
                               'end_days': [1, 2, 3, 4, 5], 'end_time': '21:30:05'}
        self.def_sched_up_2 = {'start_days': [1, 2, 3, 4, 5, 6, 7], 'start_time': '02:00:00',
                               'end_days': [1, 2, 3, 4, 5, 6, 7], 'end_time': '02:00:05'}

        self.def_sched_down_1 = {'start_days': [1, 2, 3, 4, 5], 'start_time': '08:00:00',
                                 'end_days': [1, 2, 3, 4, 5], 'end_time': '08:00:59'}
        self.def_sched_down_2 = {'start_days': [1, 2, 3, 4, 5, 6, 7], 'start_time': '01:59:00',
                                 'end_days': [1, 2, 3, 4, 5, 6, 7], 'end_time': '01:59:59'}


first_sucker = MQTTRemoteSchedule(master_topic='HomePi/Dvir/Windows/ESP32', pub_topics='HomePi/Dvir/Windows/SCHDS',
                                  device_name='SCH', msg_topic='HomePi/Dvir/Messages')
