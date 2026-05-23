from flask import Flask, request, jsonify
from flask_cors import CORS

import mysql.connector

# =========================================
# APP SETUP
# =========================================

app = Flask(__name__)

CORS(app)

# =========================================
# DATABASE CONFIG
# =========================================

db_config = {

    "host": "localhost",

    "user": "root",

    "password": "Jamayralol1!",

    "database": "FestivalSafety"
}

# =========================================
# TEST ROUTE
# =========================================


@app.route("/")
def home():

    return {

        "message": "Festival API Running"
    }

# =========================================
# GET ALL ZONES
# =========================================


@app.route("/zones", methods=["GET"])
def get_zones():

    db = mysql.connector.connect(**db_config)

    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM Zones"
    )

    zones = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(zones)

# =========================================
# GET LIVE ZONE STATUS
# =========================================


@app.route("/zone-status", methods=["GET"])
def get_zone_status():

    db = mysql.connector.connect(**db_config)

    cursor = db.cursor(dictionary=True)

    query = """

    SELECT

        Zones.Name,
        Zones.Color,

        ZoneStatus.CurrentCount,
        ZoneStatus.DensityLevel,
        ZoneStatus.UpdatedAt

    FROM ZoneStatus

    JOIN Zones
        ON ZoneStatus.ZoneID = Zones.ID

    """

    cursor.execute(query)

    data = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(data)

# =========================================
# CREATE USER
# =========================================


@app.route("/users", methods=["POST"])
def create_user():

    data = request.json

    db = mysql.connector.connect(**db_config)

    cursor = db.cursor()

    sql = """

    INSERT INTO Users

    (Name, DOB, Gender, Phone)

    VALUES (%s, %s, %s, %s)

    """

    values = (

        data["name"],
        data["dob"],
        data["gender"],
        data["phone"]
    )

    cursor.execute(sql, values)

    db.commit()

    cursor.close()
    db.close()

    return jsonify({

        "status": "success"
    })

# =========================================
# SEND DISTRESS MESSAGE
# =========================================


@app.route("/distress", methods=["POST"])
def send_distress():

    data = request.json

    db = mysql.connector.connect(**db_config)

    cursor = db.cursor()

    sql = """

    INSERT INTO EmergencyMessage

    (Message, ZoneID, SenderUserID)

    VALUES (%s, %s, %s)

    """

    values = (

        data["message"],
        data["zone_id"],
        data["user_id"]
    )

    cursor.execute(sql, values)

    db.commit()

    cursor.close()
    db.close()

    return jsonify({

        "status": "alert received"
    })

# =========================================
# GET DISTRESS MESSAGES
# =========================================


@app.route("/distress", methods=["GET"])
def get_distress():

    db = mysql.connector.connect(**db_config)

    cursor = db.cursor(dictionary=True)

    query = """

    SELECT

        EmergencyMessage.ID,
        EmergencyMessage.Message,
        EmergencyMessage.CreatedAT,

        Users.Name AS Sender,

        Zones.Name AS Zone

    FROM EmergencyMessage

    JOIN Users
        ON EmergencyMessage.SenderUserID = Users.ID

    JOIN Zones
        ON EmergencyMessage.ZoneID = Zones.ID

    ORDER BY CreatedAT DESC

    """

    cursor.execute(query)

    messages = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(messages)

# =========================================
# GET LIVE PEOPLE
# =========================================


@app.route("/people", methods=["GET"])
def get_people():

    db = mysql.connector.connect(**db_config)

    cursor = db.cursor(dictionary=True)

    cursor.execute(

        "SELECT * FROM LivePeople"
    )

    people = cursor.fetchall()

    cursor.close()
    db.close()

    return jsonify(people)
# =========================================
# RUN SERVER
# =========================================


if __name__ == "__main__":

    app.run(debug=True)
