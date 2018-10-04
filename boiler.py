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
        self.start_stop_button = tk.Button(self.frame, text="start/ Stop", command=self.on_off_cb)
        self.start_stop_button.grid(row=2, column=0)
        self.timer_button = tk.Button(self.frame, text="Timer")
        self.timer_button.grid(row=2, column=1)
        self.time_label = tk.Label(self.frame, textvariable=self.label1)
        self.time_label.grid(row=0, column=0, columnspan=2)
        self.cmd_label = tk.Label(self.frame, textvariable=self.label2)
        self.cmd_label.grid(row=1, column=0, columnspan=2)

        self.clock_update()

    def on_off_cb(self):
        if self.op_state.get() is False:
            self.label1.set("on")
            self.op_state.set(True)
        elif self.op_state.get() is True:
            self.label1.set("off")
            self.op_state.set(False)

    def time_cb(self):
        if self.op_timer.get() == 0:
            self.op_timer.set(self.op_timer.get() + 1)

    def clock_update(self):
        def update_label():
            time = str(datetime.datetime.now())[:-7]
            self.label1.set(time)

        update_label()

        root.after(500, self.clock_update)


class ClockWork:
    def __init__(self):
        pass


root = tk.Tk()
mGui = MainGUI(root)

root.mainloop()
