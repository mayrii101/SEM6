from flask import Flask, request, jsonify
from flask_cors import CORS

import mysql.connector

# =========================================
# APP SETUP
# =========================================

app = Flask(__name__)

CORS(app)

# =========================================
# DATABASE CONNECTION
# =========================================

db = mysql.connector.connect(

    host="localhost",

    user="root",

    password="Jamayralol1!",

    database="FestivalSafety"
)

cursor = db.cursor(dictionary=True)

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

    cursor.execute(

        "SELECT * FROM Zones"
    )

    zones = cursor.fetchall()

    return jsonify(zones)

# =========================================
# CREATE USER
# =========================================


@app.route("/users", methods=["POST"])
def create_user():

    data = request.json

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

    return jsonify({

        "status": "success"
    })

# =========================================
# SEND DISTRESS MESSAGE
# =========================================


@app.route("/distress", methods=["POST"])
def send_distress():

    data = request.json

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

    return jsonify({

        "status": "alert received"
    })

# =========================================
# GET DISTRESS MESSAGES
# =========================================


@app.route("/distress", methods=["GET"])
def get_distress():

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

    return jsonify(messages)

# =========================================
# RUN SERVER
# =========================================


if __name__ == "__main__":

    app.run(debug=True)
