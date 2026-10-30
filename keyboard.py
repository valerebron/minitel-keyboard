import json
import time
import RPi.GPIO as GPIO
from evdev import UInput, ecodes as e

ROWS = {
    "2": 5, "3": 6, "4": 12, "5": 13,
    "C": 16, "D": 19, "E": 20, "F": 21,
}

COLS = {
    "1": 4, "6": 17, "7": 18, "8": 22,
    "9": 23, "A": 24, "B": 25, "G": 27,
}

MAPPING_FILE = "/opt/minitel-keyboard/mapping.json"

with open(MAPPING_FILE, encoding="utf-8") as f:
    raw_mapping = json.load(f)

mapping = {}
for contact, name in raw_mapping.items():
    code = e.ecodes.get(name)
    if isinstance(code, int):
        mapping[contact] = code
    else:
        print(f"Touche ignorée : {contact} = {name}")

if not mapping:
    raise RuntimeError("Aucune touche valide dans mapping.json")

GPIO.setmode(GPIO.BCM)

for pin in ROWS.values():
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

for pin in COLS.values():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

ui = None
pressed_keys = set()
stable_contacts = set()
candidate_contacts = set()
candidate_count = 0

def scan():
    contacts = set()

    for row, pin in ROWS.items():
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(0.001)

        for col, col_pin in COLS.items():
            if GPIO.input(col_pin):
                contacts.add(f"{row}:{col}")

        GPIO.output(pin, GPIO.LOW)

    return contacts

try:
    ui = UInput(
        events={e.EV_KEY: sorted(set(mapping.values()))},
        name="Minitel 1B",
        bustype=0x03,
        vendor=0x0001,
        product=0x0001,
    )

    print("Clavier Minitel actif.", flush=True)

    while True:
        contacts = scan()

        if contacts == candidate_contacts:
            candidate_count += 1
        else:
            candidate_contacts = contacts
            candidate_count = 1

        # Filtre anti-rebond : 3 lectures identiques
        if candidate_count >= 3 and contacts != stable_contacts:
            new_keys = {
                mapping[c] for c in contacts if c in mapping
            }
            old_keys = {
                mapping[c] for c in stable_contacts if c in mapping
            }

            for key in old_keys - new_keys:
                ui.write(e.EV_KEY, key, 0)

            for key in new_keys - old_keys:
                ui.write(e.EV_KEY, key, 1)

            if old_keys != new_keys:
                ui.syn()

            stable_contacts = contacts

        time.sleep(0.005)

finally:
    if ui is not None:
        ui.close()

    GPIO.cleanup()
