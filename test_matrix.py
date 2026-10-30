import RPi.GPIO as GPIO
import time

ROWS = {
    "2": 5, "3": 6, "4": 12, "5": 13,
    "C": 16, "D": 19, "E": 20, "F": 21,
}
COLS = {
    "1": 4, "6": 17, "7": 18, "8": 22,
    "9": 23, "A": 24, "B": 25, "G": 27,
}

GPIO.setmode(GPIO.BCM)

for pin in ROWS.values():
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

for pin in COLS.values():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:
    while True:
        for row, pin in ROWS.items():
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(0.002)
            for col, col_pin in COLS.items():
                if GPIO.input(col_pin):
                    print(f"{row}:{col}", flush=True)
            GPIO.output(pin, GPIO.LOW)
        time.sleep(0.15)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()

