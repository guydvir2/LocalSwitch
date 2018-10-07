import datetime
from gpiozero import Button, OutputDevice
from time import sleep
from threading import Thread
from sys import path

modules_path = '/home/guy/github/HomePi/RPi/modules'
mqtt_path = '/home/guy/github/HomePi/RPi/MQTTswitches'
path.append(modules_path)
path.append(mqtt_path)
from use_lcd import MyLCD
from mqtt_switch import MQTTClient


class Boiler(Thread, MyLCD):
    def __init__(self, sid='hotwater_boiler', device_topic="HomePi/Dvir/WaterBoiler", msg_topic="HomePi/Dvir/Messages",
                 topic_qos=0, host="192.168.2.200", username="guy", password="kupelu9e", state_topic=None,
                 avail_topic=None):

        Thread.__init__(self)
        MyLCD.__init__(self)

        # topics
        self.msg_topic = msg_topic
        self.device_topic = device_topic
        if state_topic is None:
            self.state_topic = device_topic + "/State"
        if avail_topic is None:
            self.avail_topic = device_topic + "/Avail"

        # HW defs
        self.on_button = None
        self.timer_button = None
        self.on_button_pressed = False
        self.timer_button_pressed = False
        self.relay_1 = None
        self.on_start_time = None
        self.timer_start = None

        # parameter values
        self.lcd_line1, self.lcd_line2 = "", ""
        self.timer_counter = 0
        self.dbounceTime = 0.1
        self.max_timer_count = 12
        self.each_time_quota = 10  # mins

        # Start Service
        self.mqtt_client = MQTTClient(sid=sid, topics=[self.device_topic], topic_qos=topic_qos, host=host,
                                      msg_topic=self.msg_topic, last_will_topic=self.avail_topic,
                                      state_topic=self.state_topic, username=username, password=password)

        self.start_mqtt_service()
        self.init_gpio()
        self.off_state()

    # HW methods
    # ##########

    # Buttons callbacks
    def on_off_cb(self):
        # sleep(self.dbounceTime)
        if self.on_button_pressed is False:
            self.on_state()
        elif self.on_button_pressed is True:
            self.off_state()

    def timer_cb(self):
        # sleep(self.dbounceTime)
        if self.on_button_pressed is True:
            if self.timer_start is None:
                self.timer_start = datetime.datetime.now()
                self.timer_button_pressed = True
            if self.timer_counter <= self.max_timer_count:
                self.timer_counter += 1
            elif self.timer_counter > self.max_timer_count:
                self.timer_counter = 0
                self.timer_button_pressed = False

    # states
    def off_state(self):
        self.on_button_pressed = False
        self.relay_1.off()
        self.timer_button_pressed = False
        self.timer_counter = 0
        self.timer_start = None
        # self.on_start_time = None

    def on_state(self):
        if self.on_start_time is None:
            self.on_button_pressed = True
            self.relay_1.on()

    def init_gpio(self):
        self.on_button = Button(16)
        self.on_button.when_pressed = self.on_off_cb
        self.on_button.when_released = lambda: sleep(self.dbounceTime)

        self.timer_button = Button(26)
        self.timer_button.when_pressed = self.timer_cb
        self.timer_button.when_released = lambda: sleep(self.dbounceTime)

        self.relay_1 = OutputDevice(20, initial_value=False, active_high=True)

    # #########################

    # MQTT methods
    # ############
    def start_mqtt_service(self):
        self.mqtt_client.call_externalf = lambda: self.mqtt_commands(self.mqtt_client.arrived_msg)
        self.mqtt_client.start()
        sleep(1)

    def mqtt_commands(self, msg):
        if msg.lower() == "on":
            self.on_state()
            msg1 = '[Remote]: On'
            self.mqtt_client.pub(payload=msg.lower(), topic=self.state_topic, retain=True)
        elif msg.lower() == "off":
            self.off_state()
            msg1 = '[Remote]: Off'
            self.mqtt_client.pub(payload=msg.lower(), topic=self.state_topic, retain=True)
        else:
            msg1 = "[Remote]: Not familiar CMD"

        self.pub_msg(msg=msg1)

    def pub_msg(self, msg, topic=None):
        if topic is None:
            msg_topic = self.msg_topic
        else:
            msg_topic = topic

        device_name = 'WaterBoiler'
        time_stamp = '[' + str(datetime.datetime.now())[:-4] + ']'
        self.mqtt_client.pub(payload='%s [%s] %s' % (time_stamp, device_name, msg), topic=msg_topic)

    # ####################################

    # Thread LOOP
    #######
    def run(self):
        while True:
            t = 0
            now_time = datetime.datetime.now()

            if self.on_button_pressed is True and self.timer_button_pressed is False:
                if self.on_start_time is None:
                    self.lcd_line1 = "On"
                    self.on_start_time = datetime.datetime.now()
                    need_clear = True
                else:
                    self.lcd_line2 = str(datetime.datetime.now() - self.on_start_time)[:-5]
                    need_clear = False
            elif self.on_button_pressed is False:
                if self.on_start_time is not None:
                    self.lcd_line1 = "Total ON time"
                    self.lcd_line2 = str(datetime.datetime.now() - self.on_start_time)[:-5]
                    t = 3
                    self.on_start_time = None
                    need_clear = True
                else:
                    self.lcd_line1 = "Off"
                    self.lcd_line2 = str(now_time)[:-5]
                    need_clear = False

            elif self.timer_button_pressed is True:
                self.lcd_line1 = "ON, %d minutes" % (self.timer_counter * self.each_time_quota)
                rem_time = self.timer_start + datetime.timedelta(
                    seconds=self.timer_counter * self.each_time_quota) - datetime.datetime.now()
                self.lcd_line2 = str(rem_time)[:-5]
                if rem_time.total_seconds() <= 0:
                    self.off_state()
                    need_clear = True
            self.center_str(text1=self.lcd_line1, text2=self.lcd_line2)
            sleep(0.1 + t)
            if need_clear is True:
                self.clear_lcd()


a = Boiler()
print("Start")
a.start()
