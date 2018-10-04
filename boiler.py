import tkinter as tk
import datetime


class MainGUI(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self)
        self.master = master
        self.label1 = tk.StringVar()
        self.label2 = tk.StringVar()
        self.label1.set("First line")
        self.label2.set("OFF")
        self.op_state = tk.BooleanVar()
        self.op_state.set(False)
        self.op_timer = tk.IntVar()
        self.op_timer.set(0)
        self.frame = tk.Frame(self.master)
        self.frame.grid()
        self.start_stop_button = tk.Button(self.frame, text="Start", command=self.on_off_cb)
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

        self.off_state()

    def on_off_cb(self):
        if self.op_state.get() is False:
            self.on_state()
            self.op_state.set(True)
        elif self.op_state.get() is True:
            self.off_state()
            self.op_state.set(False)

    def time_cb(self):
        if self.op_timer.get() == 0:
            self.timer_start = datetime.datetime.now()
            self.op_timer.set(self.op_timer.get() + 1)
            self.label2.set("Timer")
            self.timer_counter()

    def clock_update(self):
        time = str(datetime.datetime.now())[:-7]
        self.label2.set(time)
        self._clock_loop = root.after(500, self.clock_update)

    def stop_clock(self):
        root.after_cancel(self._clock_loop)

    def stop_counter(self):
        root.after_cancel(self._timer_loop)

    def counter(self):
        time_delta = datetime.datetime.now() - self.on_start
        self.label2.set(str(time_delta)[:-5])
        self._timer_loop = root.after(500, self.counter)

    def timer_counter(self):
        remain_time = self.timer_start + datetime.timedelta(minutes=10 * self.op_timer.get()) - datetime.datetime.now()
        self.label2.set(str(remain_time)[:-3])
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


root = tk.Tk()
mGui = MainGUI(root)

root.mainloop()
