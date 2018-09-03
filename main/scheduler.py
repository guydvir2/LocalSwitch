import cbit
import subprocess
import getip
from sys import platform
import datetime
import os
import csv
import time


class WeeklyIntervals:
    """Class creates a datetime tuples for a recurring weekly tasks.
    Inputs: start day and time, end date and time
    Outputs: start and end datetime tuples for current week"""

    def __init__(self, day_start, time_start, day_end, time_end):
        self.day_start = day_start
        self.day_end = day_end
        self.time_start = time_start
        self.time_end = time_end

    @staticmethod
    def day_shift_time_tuple(delta_days, time1):
        """create a datetime tuple of shifted day- days and clock"""
        clock_format = '%H:%M:%S'
        clock = datetime.datetime.strptime(time1, clock_format)

        shifted_datetime = datetime.datetime.combine(
            datetime.datetime.now().date() + datetime.timedelta(days=delta_days), clock.time())
        return shifted_datetime

    def shift_from_toady_time_tuple(self, day, hour):
        shifted_datetime = self.day_shift_time_tuple(day - self.iso2h_day_convert(datetime.datetime.now().isoweekday()),
                                                     hour)
        return shifted_datetime

    @staticmethod
    def iso2h_day_convert(iso_day):
        """ convert ISO day convention to sunday=1, satureday=7"""
        if 1 <= iso_day <= 6:
            day = iso_day + 1
        elif iso_day == 7:
            day = 1
        else:
            day = None
        return day

    @staticmethod
    def h2iso_convert_day(day):
        """convert to ISO from human day numbering"""
        if 2 <= day <= 7:
            iso_day = day - 1
        elif day == 1:
            iso_day = 7
        return iso2h_day_convert

    def get_datetimes(self, future_date=None):
        start_datetime = self.shift_from_toady_time_tuple(self.day_start, self.time_start)
        # case a: end day is in same week
        if self.day_end - self.day_start >= 0:
            end_datetime = self.shift_from_toady_time_tuple(self.day_end, self.time_end)
        # case b: end day is next week
        else:
            end_datetime = self.shift_from_toady_time_tuple(self.day_end + 7, self.time_end)
        now = datetime.datetime.now()

        # optional: create future dates
        if future_date is True:
            """ when start time and end_time occured in the past:
            create future time tuple"""
            if now > start_datetime and now > end_datetime:
                end_datetime = end_datetime + datetime.timedelta(days=7)
                start_datetime = start_datetime + datetime.timedelta(days=7)

        return start_datetime, end_datetime


class RunWeeklySchedule:
    """Class gets a weekly schedule (day and time on/ off ) and in return it submits
    a status: which task is on/off and when it starts/ ends.
    inputs: lists of schedule -
    new_task={'start_days': [1, 4], 'start_time': '15:30:00', 'end_days': [5, 6], 'end_time': '22:00:00'}
    outputs: variations of on/ off status"""

    def __init__(self, on_func, off_func, sched_file=None, ext_cond=None, ext_log=None):
        self.tasks_status, self.previous_task_status, self.weekly_tasks_list = [], [], []
        self.engage_task, self.on_tasks = [], []
        self.logbook, self.ext_log = [], ext_log
        self.on_func, self.off_func, self.ext_cond = on_func, off_func, ext_cond
        self.filename = sched_file
        self.cbit = cbit.CBit(500)
        """Engage flag gives the ability to enable or disable on/off regardless"""

    def add_weekly_task(self, new_task):
        self.weekly_tasks_list.append(new_task)
        # method indicates if start an active schedule
        days = len(new_task['start_days'])
        self.engage_task.append([1] * days)
        self.previous_task_status.append([False] * days)

    def read_sched_file(self, file_in=''):
        if file_in == '':
            file_in = self.filename
        if os.path.isfile(file_in) is True:
            with open(file_in, 'r') as f:
                reader = csv.reader(f)
                self.data_from_file = list(reader)
        else:
            self.log_record('Schedule file was not found on specified location ' + str(file_in))

    def ver_tasks_descrp(self):
        # Check if schedule inputs are valid
        time_format = "%H:%M:%S"

        for i, task in enumerate(self.weekly_tasks_list):
            try:
                datetime.datetime.strptime(task['start_time'], time_format)
                datetime.datetime.strptime(task['end_time'], time_format)
            except ValueError:
                self.log_record('bad time format: ' + str(task))
                del self.weekly_tasks_list[i]
                break

            cond1 = all(list(map(lambda x: 0 < int(x) < 8, task['start_days'])))
            cond2 = all(list(map(lambda x: 0 < int(x) < 8, task['end_days'])))
            if not cond1 or not cond2:
                self.log_record('bad day format: ' + str(task))
                del self.weekly_tasks_list[i]
                break

    def convert_data_file(self):
        dict = []
        a1 = lambda a: a.split(',')
        for i, task in enumerate(self.data_from_file):
            dict.append({})
            dict[i]['start_days'] = list(map(lambda x: int(x), a1(task[0])))
            dict[i]['start_time'] = task[1]
            dict[i]['end_days'] = list(map(lambda x: int(x), a1(task[2])))
            dict[i]['end_time'] = task[3]
        return dict

    def start(self):
        # Case of reading schedule from file
        if not self.weekly_tasks_list and self.filename is not None:
            self.read_sched_file()
            self.log_record('Schedule file read successfully')
            for task in self.convert_data_file():
                self.add_weekly_task(task)

        # Case of getting schedule in code
        elif self.weekly_tasks_list:
            self.log_record('Schedule read as code arguments')

        # Neither --> QUIT
        else:
            self.log_record('Schedule not read properly. Abort!')
            quit()

        self.ver_tasks_descrp()
        self.convert_weekly_tasks_to_dates()

        # runs on CBit
        self.run_schedule()
        self.tasks_descriptive()

    def convert_weekly_tasks_to_dates(self):
        """ converts time schedule tasks  given by user to time tuples"""
        self.tasks_status = []
        for n, task in enumerate(self.weekly_tasks_list):
            self.tasks_status.append([])
            for i, day_task_start in enumerate(task['start_days']):
                self.tasks_status[-1].append([])
                status_dict = {}
                day_task_end = task['end_days'][i]
                status_dict['start'], status_dict['end'] = WeeklyIntervals(day_start=day_task_start,
                                                                           time_start=task['start_time'],
                                                                           day_end=day_task_end,
                                                                           time_end=task['end_time']).get_datetimes(
                    True)
                status_dict['state'] = False
                self.tasks_status[n][i] = status_dict.copy()

    def task_on_decision(self):
        # Run constant on CBit
        # Flags if task is "ON" or "OFF"
        for m, task in enumerate(self.tasks_status):
            for n, current_day in enumerate(task):
                if current_day['start'] <= datetime.datetime.now() <= current_day['end']:
                    self.tasks_status[m][n]['state'] = 1
                else:
                    self.tasks_status[m][n]['state'] = 0

    def run_schedule(self):  # constant run on cbit

        def act_on_change(changed_task):
            m, n = changed_task[0], changed_task[1]
            if self.tasks_status[m][n]['state'] == 1:
               self.log_record('Start Task[%d/%d]: Start %s, End %s' % (
                   m, n, self.tasks_status[m][n]['start'], self.tasks_status[m][n]['end']))
               self.on_func()
            elif self.tasks_status[m][n]['state'] == 0:
                self.off_func()
                self.log_record('End Task[%d/%d]: Start %s, End %s' % (
                   m, n, self.tasks_status[m][n]['start'], self.tasks_status[m][n]['end']))
                self.convert_weekly_tasks_to_dates()


        def check_conditions_to_switch():
            for m, task in enumerate(self.tasks_status):
                for n, sub_task in enumerate(task):

                    # detect change from last cycle of check
                    if sub_task['state'] != self.previous_task_status[m][n]:
                        act_on_change([m, n])
                    
                    self.previous_task_status[m][n] = self.tasks_status[m][n]['state']

        def inject_tasks_to_schedule():
            """ update tasks using cbit """
            self.task_on_decision()
            check_conditions_to_switch()

        self.cbit.append_process(inject_tasks_to_schedule)
        self.cbit.init_thread()

    def tasks_descriptive(self):
        for m, task in enumerate(self.tasks_status):
            for n, day in enumerate(task):
                t = [datetime.datetime.strftime(day['start'], '[%A, %H:%M:%S]'),
                     datetime.datetime.strftime(day['end'], ' - [%A, %H:%M:%S]')]
                msg = 'Task details [#%d/%d] %s %s' % (m, n, t[0], t[1])
                # print(msg)
                self.log_record(msg)
                

    def get_task_report(self, task=None):
        now = datetime.datetime.now()

        def print_report(state):

            """ SEE HOW TO UPDATE OFF TASK FOR FUTURE TIME TO ON - MOST LIKELY TO UPDATE WEEKLY INTERVALS CLASS"""
            self.log_record('Task [#%d/%d] is [%s] until [%s]' % (i, m, state, sub_task['end']))

        """AM I USING THIS FOR LOOP IN MY CODE???"""
        if task is None:
            for i, task in enumerate(self.tasks_status):
                for m, sub_task in enumerate(task):
                    if sub_task['end'] >= now >= sub_task['start']:
                        print_report('ON')
                    elif now <= sub_task['start'] or (now > sub_task['start'] and sub_task['end']):
                        print_report('OFF')
                        """THIS PART IS NEEDED FOR ONE KIND OF TASK TO SHOW"""

        else:
            sub_task = self.tasks_status[task[0]][task[1]]
            i, m = task[0], task[1]
            if sub_task['end'] >= now >= sub_task['start']:
                print_report('ON')
            elif now <= sub_task['start'] or (now > sub_task['start'] and sub_task['end']):
                print_report('OFF')

    def log_record(self, text1=''):
        time1 = str(datetime.datetime.now())[:-5]
        msg = '[%s] [%s] %s' % (time1, 'Weekly Schedule', text1)
        self.logbook.append(msg)
        # print(self.logbook[-1])
        msg1 = '[%s] %s' % ('Weekly Schedule', text1)
        if self.ext_log is not None:
            self.ext_log.log_record(msg1)


class WifiControl:
    def __init__(self):
        self.plat = platform
        print('booted on %s system' % self.plat)
        self.wifi_command = 'nmcli radio wifi'.split()
        self.pwd = None
        self.read_pwd_fromfile()

    def wifi_on_off(self, state):
        if state.upper() in ['ON', 'OFF']:
            updated_command = self.wifi_command + [state.lower()]
            a1 = subprocess.Popen(['sudo', '-S'] + updated_command, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                  universal_newlines=True)
            # a1.communicate(self.pwd + '\n')[1]

    def connect_network(self, ssid):
        updated_command = 'nmcli device wifi connect %s' % ssid
        updated_command = updated_command.split()
        a1 = subprocess.Popen(['sudo', '-S'] + updated_command, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                              universal_newlines=True)
        # a1.communicate(self.pwd + '\n')[1]

    def read_pwd_fromfile(self):
        filename = '/home/guy/Documents/github/Rpi/modules/p.txt'
        with open(filename, 'r')as f:
            self.pwd = f.read()

    def get_status(self):
        p = subprocess.Popen(['nmcli', 'radio', 'all'], stdout=subprocess.PIPE)
        # tup_output = p.communicate()
        a = []
        # time.sleep(10)
        for line in iter(p.stdout.readline, b''):
            a.append(str(line)[2:-3].split(' '))
        print(a[0][2], a[1][2])
        p.stdout.close()
        p.wait()

    def wifi_off(self):
        self.wifi_on_off('off')
        time.sleep(2)
        self.get_status()

    def wifi_on(self, ssid):
        try:
            self.wifi_on_off('on')
            self.connect_network(ssid)
            time.sleep(2)
            self.get_status()
        except OSError:
            print('NO NETWORK')
        print(self.verify_connection())

    def verify_connection(self):
        ips = getip.get_ip()
        # LAN & WAN reachable
        if ips[0] and ips[1]:
            return True
        else:
            return False


if __name__ == '__main__':
    def on_func():
        print('On function')


    def off_func():
        print('off function')


    # a = WifiControl()
    # a.wifi_on('HomeNetwork_2.4G')
    # a.wifi_off()

    #
    b = RunWeeklySchedule(on_func=on_func, off_func=off_func,
                          sched_file='/home/guy/Documents/github/Rpi/SmartHome/LocalSwitch/sched.txt')
    # # b.add_weekly_task(new_task={'start_days': [6], 'start_time': '19:03:00', 'end_days': [6], 'end_time': '23:08:00'})
    # b.add_weekly_task_weekly_task(
    #     new_task={'start_days': [3], 'start_time': '09:03:30', 'end_days': [3], 'end_time': '18:11:00'})
    # b.add_weekly_task(
    #     new_task={'start_days': [4, 7,5,7,1], 'start_time': '09:03:30', 'end_days': [1, 3,2,1,2], 'end_time': '14:35:00'})

    b.start()
