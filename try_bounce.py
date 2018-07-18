import gpiozero
from signal import pause

def print_me():
	print("on")
	
def print_me2():
	print("off")
but1 = gpiozero.Button(pin=21, pull_up=True, bounce_time=0.3)

but1.when_pressed=print_me
but1.when_released=print_me2

pause()
