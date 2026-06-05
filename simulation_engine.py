import random
import time
import mysql.connector


TOTAL_PEOPLE = 500


zones = {
    "MainStage": {"x1": 0, "x2": 40, "y1": 60, "y2": 100},
    "FoodCourt": {"x1": 60, "x2": 100, "y1": 60, "y2": 100},
    "ChillZone": {"x1": 0, "x2": 40, "y1": 0, "y2": 40},
    "Entrance": {"x1": 60, "x2": 100, "y1": 0, "y2": 40},

    "Amapiano Stage": {"x1": 0, "x2": 20, "y1": 40, "y2": 60},
    "Dancehall Stage": {"x1": 20, "x2": 40, "y1": 40, "y2": 60},
    "HipHop Stage": {"x1": 40, "x2": 60, "y1": 40, "y2": 60},
    "Notes Stage": {"x1": 60, "x2": 80, "y1": 40, "y2": 60},
    "Spotlight Stage": {"x1": 80, "x2": 100, "y1": 40, "y2": 60},

    "FoodCourt South": {"x1": 40, "x2": 60, "y1": 60, "y2": 80},
    "FoodCourt North": {"x1": 40, "x2": 60, "y1": 80, "y2": 100},

    "Toilets West": {"x1": 40, "x2": 50, "y1": 0, "y2": 20},
    "Toilets East": {"x1": 50, "x2": 60, "y1": 0, "y2": 20}
}


# zone ids
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


# db
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Jamayralol1!",
        database="FestivalSafety"
    )


# create ppl
def create_people(count=TOTAL_PEOPLE):
    people = []

    for i in range(count):

        zone = random.choice(list(zones.keys()))
        area = zones[zone]

        people.append({
            "id": i,
            "zone": zone,
            "x": random.uniform(area["x1"], area["x2"]),
            "y": random.uniform(area["y1"], area["y2"])
        })

    return people


# verandering coordinaten
def move_person(person):

    person["x"] += random.uniform(-2, 2)
    person["y"] += random.uniform(-2, 2)

    person["x"] = max(0, min(100, person["x"]))
    person["y"] = max(0, min(100, person["y"]))

    return person


# zone switching
def maybe_switch_zone(person):

    if random.random() >= 0.03:
        return person

    new_zone = random.choice(list(zones.keys()))
    area = zones[new_zone]

    person["zone"] = new_zone

    person["x"] = random.uniform(area["x1"], area["x2"])
    person["y"] = random.uniform(area["y1"], area["y2"])

    return person


# ppl per zone
def calculate_zone_counts(people):
    counts = {zone: 0 for zone in zones.keys()}

    for person in people:
        zone = person.get("zone")

        if zone in counts:
            counts[zone] += 1
        # ignore invalid zones

    return counts


# density calc
def calculate_density(count):

    if count < 45:
        return "LOW"

    if count < 55:
        return "MEDIUM"

    return "HIGH"

# update person db


def update_person_in_db(cursor, person):

    required = ["id", "zone", "x", "y"]

    if not all(k in person for k in required):
        return

    sql = """
    REPLACE INTO LivePeople
    (ID, ZoneName, X, Y, UpdatedAt)
    VALUES (%s, %s, %s, %s, NOW())
    """

    cursor.execute(sql, (
        person["id"],
        person["zone"],
        person["x"],
        person["y"]
    ))


# update zone status in db
def update_zone_status_in_db(cursor, zone_name, count):

    density = calculate_density(count)

    sql = """
    UPDATE ZoneStatus
    SET
        CurrentCount = %s,
        DensityLevel = %s,
        UpdatedAt = NOW()
    WHERE ZoneID = %s
    """

    cursor.execute(
        sql,
        (
            count,
            density,
            zone_id_map[zone_name]
        )
    )


# simulatie
def simulation_step(people, cursor):

    for person in people:

        move_person(person)

        maybe_switch_zone(person)

        update_person_in_db(
            cursor,
            person
        )

    zone_counts = calculate_zone_counts(people)

    for zone, count in zone_counts.items():

        update_zone_status_in_db(
            cursor,
            zone,
            count
        )

    return zone_counts


# zone status
def print_zone_status(zone_counts):

    for zone, count in zone_counts.items():

        density = calculate_density(count)

        print(
            f"{zone}: {count} ({density})"
        )


# run loop


def run():

    db = get_db()

    cursor = db.cursor()

    people = create_people()

    while True:

        print("\nUpdating simulation...")

        zone_counts = simulation_step(
            people,
            cursor
        )

        db.commit()

        print_zone_status(zone_counts)

        print("Database updated.")

        time.sleep(5)


if __name__ == "__main__":
    run()
