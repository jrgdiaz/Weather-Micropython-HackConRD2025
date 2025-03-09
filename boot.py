from machine import Pin

def shutup_buzzer():
    try:

        buzzer = Pin(6, Pin.OUT)
        buzzer.value(0)
        time.sleep(2)
    except Exception as e:
        print(e)

shutup_buzzer()
