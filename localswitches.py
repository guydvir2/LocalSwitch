from signal import pause
from time import sleep
from sys import platform
from sys import path
import datetime
import time
import os
import threading
from socket import gethostname

try:
    import gpiozero

    gpiozero_modules = True
except ImportError:  # ModuleNotFoundError:
    print("Fail to obtain gpiozero module")
    gpiozero_modules = False

try:
    main_path = '/home/guy/github/modules'
    path.append(main_path)
    # import my_paths
    from gmail_mod import GmailSender
    import getip
    # import use_lcd
    import scheduler

    my_modules = True

except ImportError:
    my_modules = False
    print('Fail to obtain one or more RaspberryPi modules')
    # quit()


class Output2LCD:
    """ This class outputs data to 2 lines of LCD matrix,
    parameters:
    1)switches - max of 2 lines od data
    2) ext_log - use class Log2File to save what displayed on LCD"""

    def __init__(self, switches, ext_log=None):
        self.switches = switches
        self.boot_success = False
        self.log = ext_log
        try:
            # Case of HW err
            self.lcd_display = use_lcd.MyLCD()
            self.t = threading.Thread(name='thread_disp_lcd', target=self.display_status_loop)
            self.t.start()
            self.boot_success = True
        except OSError:
            msg = "LCD hardware error"
            try:
                self.log.append_log(msg)
            except AttributeError:
                pass
            finally:
                print(msg)

    def display_status_loop(self):
        while True:
            self.disp_switch_status(time2show=3)
            self.disp_time(time2show=3)

    def disp_switch_status(self, time2show=2):
        # time to display relays status on LCD
        t1 = 0
        t_stamp = datetime.datetime.now()
        status = [[] for i in range(len(self.switches))]
        last_status = [[] for i in range(len(self.switches))]
        self.lcd_display.clear_lcd()

        while t1 < time2show:
            textonlcd = ['', '']
            for i, current_switch in enumerate(self.switches):
                # Detect change
                if last_status[i] != current_switch.switch_state[0]:
                    if current_switch.switch_state[0] is False:
                        s = 'off'
                    elif current_switch.switch_state[0] is True:
                        s = 'on '
                    status[i] = '%s :%s' % (current_switch.name, s)
                    try:
                        textonlcd[i] = str(status[i])
                        self.log.append_log(status[i], time_stamp=1)
                    except AttributeError:
                        pass
                    last_status[i] = current_switch.switch_state[0]
                    self.lcd_display.center_str(textonlcd[0], textonlcd[1])
            # take it easy :)
            time.sleep(0.5)
            t1 = (datetime.datetime.now() - t_stamp).total_seconds()

    def disp_time(self, time2show=5):
        t2 = 0
        t_stamp = datetime.datetime.now()
        self.lcd_display.clear_lcd()
        while t2 < time2show:
            time_now = str(datetime.datetime.now())[:-5].split(' ')
            self.lcd_display.center_str(text1=time_now[0], text2=time_now[1])
            t2 = (datetime.datetime.now() - t_stamp).total_seconds()


class Log2File:
    def __init__(self, filename, screen=0, time_in_log=0, name_of_master=''):
        self.path = ''
        # self.detectOS()
        self.name_of_master = name_of_master
        self.output2screen = screen
        self.time_stamp_in_log = time_in_log
        self.filename = filename  # self.path + filename
        self.check_logfile_valid()
        self.first_boot_entry()

    def time_stamp(self):
        t = str(datetime.datetime.now())[:-5]
        return t

    def detectOS(self):
        os_type = platform
        if os_type == 'darwin':
            self.path = '/Users/guy/Documents/github/Rpi/SmartHome/'
        elif os_type == 'win32':
            self.path = 'd:/users/guydvir/Documents/git/Rpi/SmartHome/'
        elif os_type == 'linux':
            self.path = '/home/guy/Documents/github/Rpi/SmartHome/'

    def first_boot_entry(self):
        # msg = 'log start @%s' % (str(platform))
        msg = '\nlog start @%s, IP:%s, OS:%s, Name:%s' % (
            gethostname(), str(getip.get_ip()[0]), platform, self.name_of_master)
        self.append_log(msg, time_stamp=0)
        self.append_log('*' * len(msg), time_stamp=0)

    def check_logfile_valid(self):
        if os.path.isfile(self.filename) is True:
            self.valid_logfile = True
        else:
            open(self.filename, 'a').close()
            self.valid_logfile = os.path.isfile(self.filename)
            if self.valid_logfile is True:
                msg = '>>Log file %s was created successfully' % self.filename
            else:
                msg = '>>Log file %s failed to create' % self.filename
            print(msg)
            self.append_log(msg, time_stamp=1)

    def append_log(self, log_entry='', time_stamp=None):
        # permanent time_stamp
        if time_stamp is None:
            if self.time_stamp_in_log == 1:
                self.msg = '[%s] %s' % (self.time_stamp(), log_entry)
            else:
                self.msg = '%s' % log_entry
        # ADHOC time_stamp - over-rides permanent one
        elif time_stamp is 1:
            self.msg = '[%s] %s' % (self.time_stamp(), log_entry)
        elif time_stamp is 0:
            self.msg = '%s' % log_entry

        if self.valid_logfile is True:
            myfile = open(self.filename, 'a')
            myfile.write(self.msg + '\n')
            myfile.close()
        else:
            print('Log err')
        if self.output2screen == 1:
            print(self.msg)


class XTractLastLogEvent:
    def __init__(self, filename):
        self.fname = filename
        self.chopped_log = ''
        self.read_logfile()

    def read_logfile(self):
        if os.path.isfile(self.fname) is True:
            with open(self.fname, 'r') as f:
                data_file = f.readlines()
                for line in reversed(data_file):
                    if 'log start' in line:
                        self.chopped_log = line + self.chopped_log
                        break
                    else:
                        self.chopped_log = line + self.chopped_log
        else:
            print('file', self.fname, ' not found')

    def xport_chopped_log(self):
        if self.chopped_log != []:
            return self.chopped_log
        else:
            return ('failed action')


class SingleSwitch:
    def __init__(self, button_pin=20, relay_pin=4, name='No-Name', mode='press', ext_log=None):
        """Relay refers to HW that makes the switch AKA "OUTPUT". Button refer to buttons physical HW AKA "INPUT" """
        self.button, self.relay = None, None
        self.button_pin = button_pin
        self.relay_pin = relay_pin
        self.valid_gpios = [4, 17, 27, 22, 5, 6, 13, 19, 26, 20, 21, 16, 12, 25, 23, 24, 18, 7]
        self.press_counter = 0
        self.name, self.mode = name, mode
        self.last_state, self.current_state = None, None
        self.logbook, self.ext_log = [], ext_log
        # case of using Single Switch in DoubleSwitch only
        self.other_SingleSwitch = None

        self.startup()

    def verify_gpio_selection(self):
        if self.button_pin in self.valid_gpios and self.relay_pin in self.valid_gpios and \
                self.button_pin != self.relay_pin:
            return 1
        else:
            self.log_record('pin definition error')
            return 0

    def startup(self):
        if self.mode in ['toggle', 'press'] and self.verify_gpio_selection() == 1:
            self.t = threading.Thread(name='thread_gpio_' + str(self.relay_pin), target=self.start_gpio_hw)
            self.t.start()
            self.log_record('init [%s mode][GPIO in/out:%s/%s] ' % (self.mode, self.button_pin, self.relay_pin))
        else:
            self.log_record('err- modes can be "toggle" or "press" only')

    def start_gpio_hw(self):
        try:
            self.button = gpiozero.Button(self.button_pin, pull_up=True)
            self.relay = gpiozero.OutputDevice(self.relay_pin)

            if self.mode == 'toggle':
                pass
                self.button.when_pressed = self.toggle_switch
            elif self.mode == 'press':
                self.button.when_pressed = self.press_switch
                self.button.when_released = self.release_switch
            self.log_record('GPIO initialize successfully')
            pause()

        except NameError:
            self.log_record("GPIO initialize fail.\nquit")
            quit()

    def press_switch(self, add=''):
        """ Press state only"""
        sleep(0.5)

        # Case of DoubleSwitch
        self.off_other_switch()
        #

        self.relay.on()
        if add == '':
            add = 'button'
        self.press_counter += 1
        msg = ('[pressed ] [%s] [%d times]' % (add, self.press_counter))
        self.log_record(msg)

    def release_switch(self, add=''):
        """ Press state only"""
        sleep(0.5)

        # Case of DoubleSwitch
        self.off_other_switch()
        #

        self.relay.off()
        if add == '':
            add = 'button'
        msg = ('[released] [%s]' % (add))
        self.log_record(msg)

    def toggle_switch(self, pressed_by='', state=None):
        """ Toggle State use in code command and Toggle mode only"""
        text = pressed_by
        self.last_state = self.relay.value
        # in case of DoubleSwitch
        self.off_other_switch()
        #
        if pressed_by == '':
            self.relay.toggle()
        elif pressed_by == 'code':
            if state == 0:
                self.relay.off()
            elif state == 1:
                self.relay.on()

        self.current_state = self.relay.value
        self.press_counter += 1
        msg = ('[%s --> %s] pressed [%s] [%d] times' % (self.last_state,
                                                        self.current_state, text, self.press_counter))
        self.log_record(msg)

    @property
    def switch_state(self):
        return [self.relay.value, self.button.value]

    """ Using for code change state- allways as toggle"""

    @switch_state.setter
    def switch_state(self, value):

        if value == 0:
            if self.relay.value is True:
                self.toggle_switch(pressed_by='code', state=value)
        elif value == 1:
            if self.relay.value is False:
                self.toggle_switch(pressed_by='code', state=value)
        else:
            msg = '[%s] must be [0,1]' % self.name
            self.log_record(msg)

    def log_record(self, text1=''):
        msg = ''
        time = str(datetime.datetime.now())[:-5]
        msg = '[%s] [%s] %s' % (time, self.name, text1)
        self.logbook.append(msg)
        print(self.logbook[-1])
        if self.ext_log is not None:
            self.ext_log.append_log(msg)
        return msg

    def add_other_switch(self, other_switch):
        """DoubleSwitch only"""
        self.other_SingleSwitch = other_switch

    def off_other_switch(self):
        """DoubleSwitch only"""
        if self.other_SingleSwitch is not None:
            if self.other_SingleSwitch.switch_state[0] is True:
                self.other_SingleSwitch.switch_state = 0
                sleep(0.3)

    def watch_dog(self):
        # run inspection in background to check state of gpios
        def run_watchdog():
            last_state = self.relay.value
            while True:
                if self.relay.value != last_state:
                    self.log_record("[WatchDog] [GPIO %s] [%s]" % (self.relay_pin, self.switch_state[0]))
                    last_state = self.relay.value
                sleep(0.1)

        sleep(1)
        self.t2 = threading.Thread(name='thread_watchdog', target=run_watchdog)
        self.t2.start()
        self.log_record('[WatchDog] init')


class DoubleSwitch:
    def __init__(self, button_pin1, button_pin2, relay_pin1, relay_pin2, mode='press', name='Double_switch',
                 sw0_name='/SW#0',
                 sw1_name='/SW#1', ext_log=None):
        self.switch0 = SingleSwitch(button_pin=button_pin1, relay_pin=relay_pin1, mode=mode, name=name + sw0_name,
                                    ext_log=ext_log)
        self.switch1 = SingleSwitch(button_pin=button_pin2, relay_pin=relay_pin2, mode=mode, name=name + sw1_name,
                                    ext_log=ext_log)
        self.switch0.add_other_switch(self.switch1)
        self.switch1.add_other_switch(self.switch0)

    def watch_dog(self):
        self.switch0.watch_dog()
        self.switch1.watch_dog()


class HomePiLocalSwitch:
    def __init__(self, switch_type, gpio_in, gpio_out, mode='press', alias='HomePi-Switch',
                 ext_log=None, sw0_name='/SW#0', sw1_name='/SW#1'):
        self.on_func, self.off_func, self.schedule, self.email = None, None, None, None
        self.gmail_recip, self.gmail_service = None, None
        self.switch_type = switch_type

        if ext_log is not None:
            self.logger = Log2File(ext_log, screen=0, time_in_log=0, name_of_master=alias)
        else:
            self.logger = None
        """ To Be UnCommented"""
        if switch_type == 'single':
            self.switch = SingleSwitch(button_pin=gpio_in, relay_pin=gpio_out, name=alias, mode=mode,
                                       ext_log=self.logger)
        elif switch_type == 'double':
            self.switch = DoubleSwitch(button_pin1=gpio_in[0], button_pin2=gpio_in[1], relay_pin1=gpio_out[0],
                                       relay_pin2=gpio_out[1], mode=mode, name=alias,
                                       sw0_name=sw0_name, sw1_name=sw1_name, ext_log=self.logger)
        else:
            self.logger.append_log(log_entry='switch type parameter wrong. select:"double" or "single". Quit.',
                                   time_stamp=1)
            quit()
        """ Up to here"""
        
        """Avoid missing time to detect GPIOs in case of instat schedule ON state command"""
        time.sleep(0.5)
        """ DO NO DELETE"""
        
    def use_watch_dog(self):
        self.switch.watch_dog()

    def weekly_schedule(self, sched_filename_0=None, local_schedule_0=None, sched_filename_1=None,
                        local_schedule_1=None):
                            
        if self.switch_type == "single":
            def on_func_0():
                self.switch.switch_state = 1

            def off_func_0():
                self.switch.switch_state = 0

            if any([sched_filename_0, local_schedule_0]):
                self.schedule_0 = scheduler.RunWeeklySchedule(on_func=on_func_0, off_func=off_func_0,
                                                              sched_file=sched_filename_0, ext_log=self.switch)
                if local_schedule_0 is not None and sched_filename_0 is None:
                    self.schedule_0.add_weekly_task(new_task=local_schedule_0)

                self.schedule_0.start()
            elif not all([sched_filename_0, local_schedule_0]):
                self.switch.switch0.log_record("No schedule was given")

        elif self.switch_type == "double":
            def on_func_0():
                self.switch.switch0.switch_state = 1

            def off_func_0():
                self.switch.switch0.switch_state = 0

            def on_func_1():
                self.switch.switch1.switch_state = 1

            def off_func_1():
                self.switch.switch1.switch_state = 0


            if any([sched_filename_0,local_schedule_0]):
                # At least one is not none
                self.schedule_0 = scheduler.RunWeeklySchedule(on_func=on_func_0, off_func=off_func_0,
                                                              sched_file=sched_filename_0, ext_log=self.switch.switch0)
                if local_schedule_0 is not None and sched_filename_0 is None:
                    self.schedule_0.add_weekly_task(new_task=local_schedule_0)

                self.schedule_0.start()
            elif not all([sched_filename_0,local_schedule_0]):
                # Both are None
                self.switch.switch0.log_record("No schedule was given")

            if any([sched_filename_1, local_schedule_1]):
                self.schedule_1 = scheduler.RunWeeklySchedule(on_func=on_func_1, off_func=off_func_1,
                                                              sched_file=sched_filename_1, ext_log=self.switch.switch1)
                if local_schedule_1 is not None and sched_filename_1 is None:
                    self.schedule_1.add_weekly_task(new_task=local_schedule_1)

                self.schedule_1.start()
            elif not all([sched_filename_1, local_schedule_1]):
                self.switch.switch1.log_record("No schedule was given")

        # Need to finish defintion of only one case is acceptable

    def gmail_defs(self, recipients, **kwargs):
        self.gmail_service = GmailSender(**kwargs)
        self.gmail_recip = recipients

    def notify_by_mail(self, subj, body):
        self.gmail_service.compose_mail(recipients=self.gmail_recip, subject=subj, body=body)

    def use_lcd(self):
        if self.switch_type == 'single':
            self.lcd = Output2LCD([self.switch])  # , ext_log=file_logger)
        elif self.switch_type == 'double':
            self.lcd = Output2LCD([self.switch.switch0, self.switch.switch1])

        if self.lcd.boot_success is True:
            self.logger.append_log(log_entry='[LCD Display] detected and loaded OK', time_stamp=1)
        else:
            self.logger.append_log(log_entry='[LCD Display] not present/ driver error', time_stamp=1)

if __name__ == "__main__":
        
    b=HomePiLocalSwitch(switch_type='single',gpio_in=21, gpio_out=16,mode='press',ext_log='/home/guy/Documents/log.log')
    b.weekly_schedule(local_schedule_0={'start_days': [3], 'start_time': '19:03:00', 'end_days': [4], 'end_time': '23:08:00'})
    
    #a = HomePiLocalSwitch(switch_type='double', gpio_in=[20, 21], gpio_out=[16, 26], mode='press',
                         #ext_log='/home/guy/Documents/log.log')
    ##a.use_watch_dog()
    ##a.use_lcd()
    #a.weekly_schedule(local_schedule_1={'start_days': [3], 'start_time': '19:03:00', 'end_days': [4], 'end_time': '23:08:00'})
    ##, sched_filename_1='/home/guy/Documents/github/Rpi/modules/sched1.txt')
    #a.gmail_defs(recipients=['guydvir.tech@gmail.com'], sender_file='/home/guy/Documents/github/Rpi/modules/ufile.txt',password_file='/home/guy/Documents/github/Rpi/modules/pfile.txt')
