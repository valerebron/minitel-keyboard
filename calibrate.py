import RPi.GPIO as GPIO
import time
import json
import os
import shutil

ROWS = {
    "2": 5, "3": 6, "4": 12, "5": 13,
    "C": 16, "D": 19, "E": 20, "F": 21,
}

COLS = {
    "1": 4, "6": 17, "7": 18, "8": 22,
    "9": 23, "A": 24, "B": 25, "G": 27,
}

# Fichier de configuration
MAPPING_FILE = "/opt/minitel/mapping.json"
BACKUP_FILE = MAPPING_FILE + ".bak"

os.makedirs(os.path.dirname(MAPPING_FILE), exist_ok=True)


def load_mapping():
    """Charge les touches existantes sans les effacer."""
    if not os.path.exists(MAPPING_FILE):
        print("Aucun mapping existant : création d'un nouveau.")
        return {}

    try:
        with open(MAPPING_FILE, "r") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("Le JSON ne contient pas un objet.")

        print(f"{len(data)} contact(s) chargé(s) depuis le mapping.")
        return data

    except (json.JSONDecodeError, ValueError) as exc:
        raise RuntimeError(
            f"Mapping invalide : {MAPPING_FILE}. "
            "Fichier conservé, aucune modification effectuée."
        ) from exc


def save_mapping(mapping):
    """Sauvegarde avec copie de sécurité et écriture atomique."""
    if os.path.exists(MAPPING_FILE):
        shutil.copy2(MAPPING_FILE, BACKUP_FILE)

    temp_file = MAPPING_FILE + ".tmp"

    with open(temp_file, "w") as f:
        json.dump(mapping, f, indent=2)
        f.write("\n")

    os.replace(temp_file, MAPPING_FILE)


def scan():
    found = set()

    for row, pin in ROWS.items():
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(0.003)

        for col, cp in COLS.items():
            if GPIO.input(cp):
                found.add(f"{row}:{col}")

        GPIO.output(pin, GPIO.LOW)

    return found


mapping = load_mapping()

GPIO.setmode(GPIO.BCM)

for pin in ROWS.values():
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

for pin in COLS.values():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:
    print("\nCalibration du clavier Minitel")
    print("Les touches existantes seront conservées.")
    print("Ctrl+C pour terminer.\n")

    while True:
        input("Appuie sur Entrée pour commencer le relevé suivant...")

        contacts = set()

        while not contacts:
            contacts = scan()
            time.sleep(0.01)

        time.sleep(0.05)
        contacts = scan()

        if not contacts:
            print("Aucun contact stable détecté. Réessaie.\n")
            continue

        print("Contact(s) détecté(s) :", ", ".join(sorted(contacts)))

        key = input(
            "Nom de la touche (ex. KEY_A, KEY_ENTER, KEY_ESC) : "
        ).strip().upper()

        if key:
            for contact in contacts:
                old_key = mapping.get(contact)

                if old_key and old_key != key:
                    print(f"{contact} : {old_key} -> {key}")

                mapping[contact] = key

            save_mapping(mapping)
            print(f"Mapping sauvegardé : {len(mapping)} contact(s).\n")
        else:
            print("Aucune modification.\n")

        while scan():
            time.sleep(0.02)

except KeyboardInterrupt:
    print("\nCalibration terminée.")

finally:
    GPIO.cleanup()

