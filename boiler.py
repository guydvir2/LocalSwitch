import tkinter as tk
import datetime
from time import sleep


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
        self.timer_button = tk.Button(self.frame, text="Timer", command=self.timer_cb)
        self.timer_button.grid(row=2, column=1)
        self.time_label = tk.Label(self.frame, textvariable=self.label1)
        self.time_label.grid(row=0, column=0, columnspan=2)
        self.cmd_label = tk.Label(self.frame, textvariable=self.label2)
        self.cmd_label.grid(row=1, column=0, columnspan=2)

        self.on_start_time = None
        self.timer_start = None
        self._clock_loop_id = None
        self._counter_loop_id = None
        self._timer2_loop_id = None
        self.timeRemain_counter = None

        self.off_state()

    # Buttons callbacks
    def on_off_cb(self):
        if self.op_state.get() is False:
            self.on_state()
            self.op_state.set(True)
        elif self.op_state.get() is True:
            self.off_state()

    def timer_cb(self):
        if self.op_state.get() is True:
            self.label1.set("On with Timer (%d minutes"%((self.op_timer.get()+1)*10))
            if self.op_timer.get() == 0:
                self.timer_start = datetime.datetime.now()
                self.op_timer.set(self.op_timer.get() + 1)
                self.stop_clock()
                self.stop_on_counter()
                self.start_timer()
            elif 12 >= self.op_timer.get() > 0:
                self.op_timer.set(self.op_timer.get() + 1)
            elif self.op_timer.get() > 13:
                self.op_timer.set(0)
                self.stop_timer()
                self.on_state()

    # states
    def off_state(self):
        self.op_state.set(False)
        if self._counter_loop_id is not None:
            self.stop_on_counter()

        if self.on_start_time is not None:
            try:
                if (datetime.datetime.now() - self.on_start_time).total_seconds() > 3:
                    self.label1.set("Total ON time:")
                    self.label2.set(str(datetime.datetime.now() - self.on_start_time)[:-5])
                    self.on_start_time = None
                    sleep(5)
            except AttributeError:
                pass
        self.label1.set("Off")
        self.run_clock()

    def on_state(self):
        if self.on_start_time is None:
            self.on_start_time = datetime.datetime.now()
        self.label1.set("On")
        self.stop_clock()
        self.start_on_counter()

    def turn_off_device(self):
        self.off_state()

    # clock displayed when state is OFF
    def run_clock(self):
        time = str(datetime.datetime.now())[:-7]
        self.label2.set(time)
        self._clock_loop_id = root.after(500, self.run_clock)

    def stop_clock(self):
        root.after_cancel(self._clock_loop_id)

    # count ON time
    def start_on_counter(self):
        time_delta = datetime.datetime.now() - self.on_start_time
        self.label2.set(str(time_delta)[:-5])
        self._counter_loop_id = root.after(500, self.start_on_counter)

    def stop_on_counter(self):
        root.after_cancel(self._counter_loop_id)
        self._counter_loop_id = None

    # Display timer time
    def start_timer(self):
        def run():
            self.timeRemain_counter = self.timer_start + datetime.timedelta(
                seconds=5 * self.op_timer.get()) - datetime.datetime.now()

            if self.timeRemain_counter.total_seconds() > 0:
                self.label2.set(str(self.timeRemain_counter)[:-5])
            else:
                self.op_timer.set(0)

        if self.op_timer.get() > 0:
            run()
            self._timer2_loop_id = root.after(500, self.start_timer)

        else:
            self.timeRemain_counter = None
            self.stop_timer()
            self.turn_off_device()
            self.op_timer.set(0)

    def stop_timer(self):
        root.after_cancel(self._timer2_loop_id)
        self._timer2_loop_id = None


root = tk.Tk()
mGui = MainGUI(root)

root.mainloop()
