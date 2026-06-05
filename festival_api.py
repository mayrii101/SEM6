from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

# 🔒 Limit request size (prevents huge payload attacks)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1MB

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Jamayralol1!",
    "database": "FestivalSafety"
}

# =========================================
# DB
# =========================================


def get_db():
    return mysql.connector.connect(**db_config)

# =========================================
# VALIDATION HELPERS
# =========================================


def is_valid_string(value):
    return isinstance(value, str) and value.strip() != ""


def validate_user(data):
    if not data:
        return False, "Missing JSON"

    required = ["name", "dob", "gender", "phone"]

    for field in required:
        if field not in data:
            return False, f"Missing field: {field}"

    if not all(is_valid_string(data.get(f)) for f in required):
        return False, "Invalid data types"

    return True, None


def validate_distress(data):
    if not data:
        return False, "Missing JSON"

    required = ["message", "zone_id", "user_id"]

    for field in required:
        if field not in data:
            return False, f"Missing field: {field}"

    if not is_valid_string(data.get("message")):
        return False, "Invalid message"

    return True, None


# =========================================
# HOME
# =========================================

@app.route("/")
def home():
    return {"message": "Festival API Running"}


# =========================================
# ZONES
# =========================================

@app.route("/zones", methods=["GET"])
def get_zones():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM Zones")
        zones = cursor.fetchall()

        cursor.close()
        db.close()

        return jsonify(zones), 200

    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 400


# =========================================
# ZONE STATUS
# =========================================

@app.route("/zone-status", methods=["GET"])
def get_zone_status():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = """
        SELECT Zones.Name, Zones.Color,
               ZoneStatus.CurrentCount,
               ZoneStatus.DensityLevel,
               ZoneStatus.UpdatedAt
        FROM ZoneStatus
        JOIN Zones ON ZoneStatus.ZoneID = Zones.ID
        """

        cursor.execute(query)
        data = cursor.fetchall()

        cursor.close()
        db.close()

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 400


# =========================================
# CREATE USER
# =========================================

@app.route("/users", methods=["POST"])
def create_user():
    try:
        data = request.get_json(silent=True)

        valid, error = validate_user(data)
        if not valid:
            return jsonify({"error": error}), 400

        db = get_db()
        cursor = db.cursor()

        sql = """
        INSERT INTO Users (Name, DOB, Gender, Phone)
        VALUES (%s, %s, %s, %s)
        """

        cursor.execute(sql, (
            data["name"],
            data["dob"],
            data["gender"],
            data["phone"]
        ))

        db.commit()
        cursor.close()
        db.close()

        return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 400


# =========================================
# DISTRESS POST
# =========================================

@app.route("/distress", methods=["POST"])
def send_distress():
    try:
        data = request.get_json(silent=True)

        valid, error = validate_distress(data)
        if not valid:
            return jsonify({"error": error}), 400

        db = get_db()
        cursor = db.cursor()

        sql = """
        INSERT INTO EmergencyMessage (Message, ZoneID, SenderUserID)
        VALUES (%s, %s, %s)
        """

        cursor.execute(sql, (
            data["message"],
            data["zone_id"],
            data["user_id"]
        ))

        db.commit()
        cursor.close()
        db.close()

        return jsonify({"status": "alert received"}), 200

    except Exception as e:
        return jsonify({"error": "Server error", "details": str(e)}), 400


# =========================================
# GET DISTRESS
# =========================================

@app.route("/distress", methods=["GET"])
def get_distress():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        query = """
        SELECT EmergencyMessage.ID,
               EmergencyMessage.Message,
               EmergencyMessage.CreatedAT,
               Users.Name AS Sender,
               Zones.Name AS Zone
        FROM EmergencyMessage
        JOIN Users ON EmergencyMessage.SenderUserID = Users.ID
        JOIN Zones ON EmergencyMessage.ZoneID = Zones.ID
        ORDER BY CreatedAT DESC
        """

        cursor.execute(query)
        messages = cursor.fetchall()

        cursor.close()
        db.close()

        return jsonify(messages), 200

    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 400


# =========================================
# PEOPLE
# =========================================

@app.route("/people", methods=["GET"])
def get_people():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM LivePeople")
        people = cursor.fetchall()

        cursor.close()
        db.close()

        return jsonify(people), 200

    except Exception as e:
        return jsonify({"error": "Database error", "details": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
