import tkinter as tk
import datetime


class MainGUI(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self)
        self.master = master
        self.master.title("HotWater Boiler Controller")
        self.label1 = tk.StringVar()
        self.label2 = tk.StringVar()

        self.op_state = tk.BooleanVar()
        self.op_state.set(False)
        self.op_timer = tk.IntVar()
        self.op_timer.set(0)

        self.frame = tk.Frame(self.master)
        self.frame.grid()
        self.start_stop_button = tk.Button(self.frame, text="Start", command=self.on_off_cb, width=15)
        self.start_stop_button.grid(row=2, column=0)
        self.timer_button = tk.Button(self.frame, text="Timer", command=self.time_cb)
        self.timer_button.grid(row=2, column=1)
        self.time_label = tk.Label(self.frame, textvariable=self.label1)
        self.time_label.grid(row=0, column=0, columnspan=2)
        self.cmd_label = tk.Label(self.frame, textvariable=self.label2)
        self.cmd_label.grid(row=1, column=0, columnspan=2)
        self.on_start = None
        self.timer_start = None
        self._clock_loop = None
        self._timer_loop = None
        self._timer2_loop = None
        self.timeRemain_counter = None

        self.off_state()

    def on_off_cb(self):
        if self.op_state.get() is False:
            self.on_state()
            self.op_state.set(True)
        elif self.op_state.get() is True:
            self.off_state()
            self.op_state.set(False)

    def time_cb(self):
        if self.op_state.get() is True:
            if self.op_timer.get() == 0:
                self.timer_start = datetime.datetime.now()
                self.label1.set("On + Timer")
                self.op_timer.set(self.op_timer.get() + 1)
                self.stop_clock()
                self.stop_counter()
                self.timer_counter()
            elif 12 >= self.op_timer.get() > 0:
                self.op_timer.set(self.op_timer.get() + 1)
            elif self.op_timer.get() > 13:
                self.op_timer.set(0)

    def clock_update(self):
        time = str(datetime.datetime.now())[:-7]
        self.label2.set(time)
        self._clock_loop = root.after(500, self.clock_update)

    def stop_clock(self):
        root.after_cancel(self._clock_loop)

    def stop_counter(self):
        root.after_cancel(self._timer_loop)

    def stop_timer(self):
        root.after_cancel(self._timer2_loop)
        print("STOP TIMER")

    def counter(self):
        time_delta = datetime.datetime.now() - self.on_start
        self.label2.set(str(time_delta)[:-5])
        self._timer_loop = root.after(500, self.counter)

    def timer_counter(self):
        def run():
            self.timeRemain_counter = self.timer_start + datetime.timedelta(
                seconds=10 * self.op_timer.get()) - datetime.datetime.now()
            self.label2.set(str(self.timeRemain_counter)[:-5])

        if self.op_timer.get() > 0 and self.timeRemain_counter.total_seconds() > 0:
            print("RUN")
            run()
        elif self.timeRemain_counter.total_seconds() <= 0:
            self.timeRemain_counter = None
            self.stop_timer()
            self.turn_off_device()
            self.op_timer.set(0)
        self._timer2_loop = root.after(500, self.timer_counter)

    def off_state(self):
        self.label1.set("Off")
        self.clock_update()
        if self._timer_loop is not None:
            self.stop_counter()

    def on_state(self):
        self.on_start = datetime.datetime.now()
        self.label1.set("On")
        self.stop_clock()
        self.counter()

    def turn_off_device(self):
        root.after_cancel(self._timer2_loop)
        self.off_state()


root = tk.Tk()
mGui = MainGUI(root)

root.mainloop()
