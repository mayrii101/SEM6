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
    }
}

# =========================================
# CREATE PEOPLE
# =========================================

TOTAL_PEOPLE = 200

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
        "Entrance": 0
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
        "Entrance": 4
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
