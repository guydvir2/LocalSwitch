import datetime
from gpiozero import Button, OutputDevice
from time import sleep
from threading import Thread
from sys import path
modules_path = '/home/guy/github/modules'
path.append(modules_path)
from use_lcd import MyLCD

class Boiler(Thread, MyLCD): 
    def __init__(self):
        Thread.__init__(self)
        MyLCD.__init__(self)
        self.boot_test()
        self.on_start_time = None
        self.timer_start = None
        self.timeRemain_counter = None
        self.allowed_timer_press = 12
        self.each_time_quota = 10  # mins
        self.on_button_pressed = False
        self.timer_button_pressed = False
        self.line1, self.line2 = "",""
        
        self.init_gpio()
        self.on_state()

    def init_gpio(self):
        self.on_button = Button(16)
        self.on_button.when_pressed = self.on_off_cb
        
        self.timer_button = Button(26)
        self.timer_button.when_pressed = self.timer_cb

        self.relay_1 = OutputDevice(20,initial_value=False, active_high=False)

    def run(self):
        while True:
            now_time = datetime.datetime.now()
            if self.on_button_pressed is True:
                self.line1 = "On"
                self.line2 = str(datetime.datetime.now()-self.on_start_time)[:-5]
            elif self.on_button_pressed is False:
                self.line1 = "Off"
                self.line2=str(now_time)[:-5]

            self.center_str(text1=self.line1, text2=self.line2)
            sleep(0.1)
    # Buttons callbacks
    def on_off_cb(self):
        if self.op_state.get() is False:
            self.on_state()
            self.op_state.set(True)
        elif self.op_state.get() is True:
            self.off_state()

    def timer_cb(self):
        if self.op_state.get() is True:
            # self.label1.set("On with Timer (%d minutes" % ((self.op_timer.get() + 1) * self.each_time_quota))
            print("On with Timer (%d minutes" % ((self.op_timer.get() + 1) * self.each_time_quota))
            if self.op_timer.get() == 0:
                self.timer_start = datetime.datetime.now()
                self.op_timer.set(self.op_timer.get() + 1)
                self.stop_clock()
                self.stop_on_counter()
                self.start_timer()
            elif self.allowed_timer_press >= self.op_timer.get() > 0:
                self.op_timer.set(self.op_timer.get() + 1)
            elif self.op_timer.get() == self.allowed_timer_press + 1:
                self.op_timer.set(0)
                self.stop_timer()
                self.on_state()

    # states
    def off_state(self):
        self.on_button_pressed = False
        self.relay_1.off()
        # if self.on_start_time is not None:
        #     print("enter on start")
        #     try:
        #         if (datetime.datetime.now() - self.on_start_time).total_seconds() > 3:
        #             print("resetting")
        #             self.label1.set("Total ON time:")
        #             t = str(datetime.datetime.now() - self.on_start_time)[:-5]
        #             print("Total ON time: %s" % t)
        #             self.label2.set("GUY")
        #     except AttributeError:
        #         print("ERROR")
        # 

        # self.label1.set("Off")
        self.on_start_time = None

    def on_state(self):
        if self.on_start_time is None:
            self.on_start_time = datetime.datetime.now()
            self.on_button_pressed= True
            self.relay_1.on()
        print("On")

    def turn_off_device(self):
        self.off_state()

    # clock displayed when state is OFF
    def run_clock(self):
        time = str(datetime.datetime.now())[:-7]
        # self.label2.set(time)
        print(time)
        # self._clock_loop_id = root.after(500, self.run_clock)

    def stop_clock(self):
        pass
        # root.after_cancel(self._clock_loop_id)

    # count ON time
    def start_on_counter(self):
        time_delta = datetime.datetime.now() - self.on_start_time
        # self.label2.set(str(time_delta)[:-5])
        print(str(time_delta)[:-5])
        # self._counter_loop_id = root.after(500, self.start_on_counter)

    def stop_on_counter(self):
        root.after_cancel(self._counter_loop_id)
        self._counter_loop_id = None

    # Display timer time
    def start_timer(self):
        def run():
            self.timeRemain_counter = self.timer_start + datetime.timedelta(
                seconds=self.each_time_quota * self.op_timer.get()) - datetime.datetime.now()

            if self.timeRemain_counter.total_seconds() > 0:
                # self.label2.set(str(self.timeRemain_counter)[:-5])
                print(str(self.timeRemain_counter)[:-5])
            else:
                self.op_timer.set(0)

        if self.op_timer.get() > 0:
            run()
            # self._timer2_loop_id = root.after(500, self.start_timer)

        else:
            self.timeRemain_counter = None
            self.stop_timer()
            self.turn_off_device()
            self.op_timer.set(0)

a = Boiler()
print("Start")
a.start()
