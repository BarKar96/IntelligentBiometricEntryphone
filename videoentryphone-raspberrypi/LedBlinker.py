import time
import RPi.GPIO as GPIO


def blink(led_color):
    gpio_pin = None
    if led_color == "GREEN":
        gpio_pin = 37
    if led_color == "RED":
        gpio_pin = 33
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(gpio_pin,GPIO.OUT)
    GPIO.output(gpio_pin,True)
    time.sleep(4)
    GPIO.output(gpio_pin,False)


#blink("GREEN")