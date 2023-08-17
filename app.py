import os
import psycopg2
from datetime import datetime, timezone
from dotenv import load_dotenv 
from flask import Flask, request

#queries
CREATE_ROOMS_TABLE = (
    "CREATE TABLE IF NOT EXISTS rooms (id SERIAL PRIMARY KEY, name TEXT);"

)
CREATE_TEMPS_TABLE = (
    "CREATE TABLE IF NOT EXISTS temperatures (room_id INTEGER, temperature REAL,date TIMESTAMP, FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE);"

)
INSET_ROOM_RETURN_ID = "INSERT INTO rooms (name) VALUES (%s) RETURNING (id);"
INSERT_INTO_TEMPERATURES = "INSERT INTO temperatures (room_id, temperature,date) VALUES (%s, %s, %s);"

GLOBAL_NUMBER_OF_DAYS = (
    "SELECT COUNT(DISTINCT DATE(date)) AS days FROM temperatures;"

)

GLOBAL_AVG = (
    "SELECT AVG(temperature) AS average FROM temperatures;"
)





load_dotenv()


app = Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)


@app.post("/api/room")
def create_room():
    data = request.get_json()
    name = data['name']
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_ROOMS_TABLE)
            cursor.execute(INSET_ROOM_RETURN_ID, (name,))
            room_id = cursor.fetchone()[0] #gives the id
    return {'id': room_id, "message": f"Room {name} created."}, 201


@app.post("/api/temperature")
def add_temp():
    data = request.get_json()
    temperature = data["temperature"]
    room_id = data['room']

    try:
        date = datetime.strptime(data['date'], "%m-%d-%Y %H:%M:%S")
    except KeyError:
        date = datetime.now(timezone.utc)
    
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_TEMPS_TABLE)
            cursor.execute(INSERT_INTO_TEMPERATURES, (room_id, temperature, date))
        
        return {"message":"temperature added successfuly"}, 201
    

@app.get("/api/average")
def get_avg():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(GLOBAL_AVG)
            average = cursor.fetchone()[0]
            cursor.execute(GLOBAL_NUMBER_OF_DAYS)
            days = cursor.fetchone()[0]
        return {"average temps:":round(average, 2), "Unique days are:":days}