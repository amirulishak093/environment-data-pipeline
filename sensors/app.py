from datetime import datetime
import threading
import time
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, Column, Float, Integer, String, DateTime
import pandas as pd

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
db = SQLAlchemy(app)

# Lock for synchronizing database access
db_lock = threading.Lock()


class Data(db.Model):
    id = Column(Integer, primary_key=True)
    co = Column(Float)
    humidity = Column(Float)
    light = Column(Boolean)
    lpg = Column(Float)
    motion = Column(Boolean)
    smoke = Column(Float)
    temp = Column(Float)
    device = Column(String)
    ts = Column(DateTime)


# Drop all tables and create new ones upon initialization
def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()


def run_sensor(device):
    print(device)
    df = pd.read_csv(f"./data/{device}_data.csv")

    def process_row(row):
        with app.app_context():
            with db_lock:
                data = Data(
                    co=row["co"],
                    humidity=row["humidity"],
                    light=row["light"],
                    lpg=row["lpg"],
                    motion=row["motion"],
                    smoke=row["smoke"],
                    device=device,
                    temp=row["temp"],
                    ts=datetime.now(),
                )
                db.session.add(data)
                db.session.commit()

        time.sleep(5)

    df.apply(process_row, axis=1)


@app.route("/")
def home():
    return "Data addition in progress."


@app.route("/data", methods=["GET"])
def get_data():
    device = request.args.get("device")
    if device:
        with db_lock:
            data = Data.query.filter_by(device=device).order_by(Data.ts.desc()).first()
            if data:
                return jsonify(
                    {
                        "device": device,
                        "co": data.co,
                        "humidity": data.humidity,
                        "light": data.light,
                        "lpg": data.lpg,
                        "motion": data.motion,
                        "smoke": data.smoke,
                        "temp": data.temp,
                        "ts": data.ts.strftime("%Y-%m-%dT%H:%M:%S") + "Z",
                    }
                )
    return jsonify({})


if __name__ == "__main__":
    init_db()

    devices = ["00:0f:00:70:91:0a", "b8:27:eb:bf:9d:51", "1c:bf:ce:15:ec:4d"]
    threads = {}

    # Run each sensors in a new thread
    for device in devices:
        threads[device] = threading.Thread(
            target=run_sensor, daemon=True, args=[device]
        )
        threads[device].start()

    app.run(host="0.0.0.0", port=2800)
