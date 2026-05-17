import serial
import time
import random

# ESP32 connection

PORT = '/dev/cu.usbserial-0001'
esp32 = serial.Serial(PORT, 115200)

time.sleep(2)

# zones

zones = [
    "MainStage",
    "FoodCourt",
    "ChillZone",
    "Entrance"
]


# fake ppl

people = []

TOTAL_PEOPLE = 200

for i in range(TOTAL_PEOPLE):
    person = {
        "id": i,
        "zone": random.choice(zones)
    }

    people.append(person)


# echte hardware (armband)

real_bracelet = {
    "id": 999,
    "zone": "MainStage"
}


# main loop

while True:

    # Randomly move fake people
    for person in people:

        # 30% chance to move
        if random.random() < 0.3:
            person["zone"] = random.choice(zones)

    # Randomly move real bracelet
    if random.random() < 0.5:
        real_bracelet["zone"] = random.choice(zones)

    # Count people in zones
    zone_counts = {}

    for zone in zones:
        zone_counts[zone] = 0

    for person in people:
        zone_counts[person["zone"]] += 1

    # Get bracelet zone
    current_zone = real_bracelet["zone"]

    people_in_zone = zone_counts[current_zone]

    # Determine density state
    if people_in_zone < 45:
        state = "LOW"

    elif people_in_zone < 55:
        state = "MEDIUM"

    else:
        state = "HIGH"

    # stuur naar esp32

    esp32.write((state + "\n").encode())

    # output debug

    print("\n====================")

    print(f"Bracelet Zone: {current_zone}")
    print(f"People in Zone: {people_in_zone}")
    print(f"State Sent: {state}")

    print("\nZone Counts:")

    for zone, count in zone_counts.items():
        print(f"{zone}: {count}")

    time.sleep(5)
