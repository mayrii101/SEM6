import random
import time
import mysql.connector

# =========================================
# DATABASE CONNECTION
# =========================================

db = mysql.connector.connect(

    host="localhost",

    user="root",

    password="Jamayralol1!",

    database="FestivalSafety"
)

cursor = db.cursor()

# =========================================
# ZONES
# =========================================

zones = {

    "MainStage": {
        "x1": 0,
        "x2": 40,
        "y1": 60,
        "y2": 100
    },

    "FoodCourt": {
        "x1": 60,
        "x2": 100,
        "y1": 60,
        "y2": 100
    },

    "ChillZone": {
        "x1": 0,
        "x2": 40,
        "y1": 0,
        "y2": 40
    },

    "Entrance": {
        "x1": 60,
        "x2": 100,
        "y1": 0,
        "y2": 40
    },

    # ───────── Middle band (y: 40–60) ─────────

    "Amapiano Stage": {
        "x1": 0,
        "x2": 20,
        "y1": 40,
        "y2": 60
    },

    "Dancehall Stage": {
        "x1": 20,
        "x2": 40,
        "y1": 40,
        "y2": 60
    },

    "HipHop Stage": {
        "x1": 40,
        "x2": 60,
        "y1": 40,
        "y2": 60
    },

    "Notes Stage": {
        "x1": 60,
        "x2": 80,
        "y1": 40,
        "y2": 60
    },

    "Spotlight Stage": {
        "x1": 80,
        "x2": 100,
        "y1": 40,
        "y2": 60
    },

    # ───────── Extra facilities ─────────

    "FoodCourt South": {
        "x1": 40,
        "x2": 60,
        "y1": 60,
        "y2": 80
    },

    "FoodCourt North": {
        "x1": 40,
        "x2": 60,
        "y1": 80,
        "y2": 100
    },

    "Toilets West": {
        "x1": 40,
        "x2": 50,
        "y1": 0,
        "y2": 20
    },

    "Toilets East": {
        "x1": 50,
        "x2": 60,
        "y1": 0,
        "y2": 20
    }
}

# =========================================
# CREATE PEOPLE
# =========================================

TOTAL_PEOPLE = 500

people = []

for i in range(TOTAL_PEOPLE):

    zone = random.choice(
        list(zones.keys())
    )

    area = zones[zone]

    people.append({

        "id": i,

        "zone": zone,

        "x": random.uniform(
            area["x1"],
            area["x2"]
        ),

        "y": random.uniform(
            area["y1"],
            area["y2"]
        )
    })

# =========================================
# MAIN LOOP
# =========================================

while True:

    print("\nUpdating simulation...")

    zone_counts = {
        "MainStage": 0,
        "FoodCourt": 0,
        "ChillZone": 0,
        "Entrance": 0,

        "Amapiano Stage": 0,
        "Dancehall Stage": 0,
        "HipHop Stage": 0,
        "Notes Stage": 0,
        "Spotlight Stage": 0,

        "FoodCourt South": 0,
        "FoodCourt North": 0,

        "Toilets West": 0,
        "Toilets East": 0
    }

    # Move people

    for person in people:

        person["x"] += random.uniform(-2, 2)

        person["y"] += random.uniform(-2, 2)

        person["x"] = max(
            0,
            min(100, person["x"])
        )

        person["y"] = max(
            0,
            min(100, person["y"])
        )

        # Random zone switch

        if random.random() < 0.03:

            new_zone = random.choice(
                list(zones.keys())
            )

            area = zones[new_zone]

            person["zone"] = new_zone

            person["x"] = random.uniform(
                area["x1"],
                area["x2"]
            )

            person["y"] = random.uniform(
                area["y1"],
                area["y2"]
            )

        zone_counts[person["zone"]] += 1

        # Update LivePeople table

        sql = """

        REPLACE INTO LivePeople

        (ID, ZoneName, X, Y, UpdatedAt)

        VALUES (%s, %s, %s, %s, NOW())

        """

        values = (

            person["id"],
            person["zone"],
            person["x"],
            person["y"]
        )

        cursor.execute(sql, values)

    # Update ZoneStatus table

    zone_id_map = {

        "MainStage": 1,
        "FoodCourt": 2,
        "ChillZone": 3,
        "Entrance": 4,
        "Amapiano Stage": 5,
        "Dancehall Stage": 6,
        "HipHop Stage": 7,
        "Notes Stage": 8,
        "Spotlight Stage": 9,
        "FoodCourt South": 10,
        "Toilets West": 11,
        "Toilets East": 12,
        "FoodCourt North": 13
    }

    for zone, count in zone_counts.items():

        if count < 45:

            density = "LOW"

        elif count < 55:

            density = "MEDIUM"

        else:

            density = "HIGH"

        update_sql = """

        UPDATE ZoneStatus

        SET

            CurrentCount = %s,
            DensityLevel = %s,
            UpdatedAt = NOW()

        WHERE ZoneID = %s

        """

        values = (

            count,
            density,
            zone_id_map[zone]
        )

        cursor.execute(update_sql, values)

        print(
            f"{zone}: {count} ({density})"
        )

    db.commit()

    print("Database updated.")

    time.sleep(5)
