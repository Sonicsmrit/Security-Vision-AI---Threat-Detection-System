from deepface import DeepFace
import pickle as pk
import sqlite3 as sq
from datetime import datetime, timedelta
import csv

with open("Data Files/index.txt", "r") as img_ind:
    index = int(img_ind.read().strip())

def extract_features(img): ##extracts the vector data of the image
    if img is None:
        return None
    try:
        embedding = DeepFace.represent(
            img_path= img,
            model_name="Facenet",
            enforce_detection=False
        )
        return embedding[0]["embedding"]
    except Exception as e: 
        return None

def load_database(): ##loads the database
    try:
        with open("Data Files/face_db.pkl", "rb") as f:
                return pk.load(f)
    except:
        return {} 

def database(face_crop, username): ##puts data into the database
    global index

    data_dict = load_database()
    
    with open("Data Files/face_db.pkl", "wb") as f: #opens the pkl database the put the binary
        
        features = extract_features(face_crop)
        User_name = username

        if features is None:
            print("Face not detected. User not saved.")
            return data_dict


        data_dict[f"{User_name}"] = features

        index += 1

        with open("Data Files/index.txt", "w") as img_ind: #puts the index number
            img_ind.write(str(index))


        pk.dump(data_dict, f)

    return data_dict



def record(name): ##database to record people who have been seen on the camera and when(attendence record)
    current_time = datetime.now()
    formatted_time = current_time.strftime("%I:%M %p")
    formatted_date = current_time.strftime("%Y-%m-%d")

    
    values = {
        'Name': name,
        'Date': formatted_date,
        'Time': formatted_time,
        'Status': "present"
    }

    with open("Data Files/record.csv", "r") as val: #open the csv to read the entries
        reader = csv.DictReader(val)
        records_atp = list(reader)
        
        for atp in records_atp:
            if atp['Name'] == values['Name'] and atp['Date'] == values['Date']: ##check so there arent duplicate enteries in the same day
                return 0


    with open("Data Files/record.csv", "a", newline="") as f: #open the csv to write in it
        write_values = csv.DictWriter(f, fieldnames=["Name","Date","Time","Status"])
        write_values.writerow(values)


def threat(threat_level, person_name, weapon_detected, confidence, screenshotpath):

    current_time = datetime.now()
    formatted_time = current_time.strftime("%I:%M %p")
    formatted_date = current_time.strftime("%Y-%m-%d")


    database_file = 'threat_data_dashboard.db'
    conn = sq.connect(database_file)

    data_entry = (formatted_time, formatted_date, threat_level, person_name, weapon_detected, confidence, screenshotpath)

    cursor = conn.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS detect(id INTEGER PRIMARY KEY AUTOINCREMENT, " \
    "timestamp TEXT," \
    " date TEXT," \
    " threat_level TEXT," \
    "  person_name TEXT," \
    " weapon_detected TEXT," \
    " confidence FLOAT," \
    " screenshot_path TEXT)")

    cursor.execute("SELECT timestamp, threat_level FROM detect ORDER BY id DESC LIMIT 1")
    last_entry = cursor.fetchone()

    insert = True

    if last_entry:

        last_entry_time, previous_threat = last_entry

        last_time = datetime.strptime(last_entry_time, "%I:%M %p")
        last_time = last_time.replace(
            year=current_time.year,
            month=current_time.month,
            day=current_time.day
        )
        current_timing = datetime.now()

        if current_timing - last_time < timedelta(minutes=1) and threat_level == previous_threat:
            insert = False
        
        
    if insert:
        cursor.execute("""
        INSERT INTO detect
        (timestamp, date, threat_level, person_name, weapon_detected, confidence, screenshot_path)
        VALUES(?,?,?,?,?,?,?)
        """, data_entry)

    conn.commit()
    conn.close()



def get_database():
    
    conn = sq.connect('threat_data_dashboard.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM detect")
    rows = cursor.fetchall()
    conn.close()

    return rows

def dashboard(date):

    database_file = 'threat_data_dashboard.db'
    conn = sq.connect(database_file)
    cursor = conn.cursor()

    cursor.execute("SELECT count(*) FROM detect WHERE date=?", (date,))
    total_detect = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM detect WHERE date=? AND threat_level='RED'",(date,))
    total_red = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM detect WHERE date=? AND threat_level='YELLOW'", (date,))
    total_yellow = cursor.fetchone()[0]

    cursor.execute("SELECT count(*) FROM detect WHERE date=? AND threat_level='GREEN'", (date,))
    total_green = cursor.fetchone()[0]

    cursor.execute("SELECT person_name FROM detect WHERE date=? AND threat_level='GREEN'", (date,))
    names = cursor.fetchall()

    cursor.execute("SELECT screenshot_path FROM detect WHERE date=?", (date,))
    screenshots = cursor.fetchall()

    return {
        'total':total_detect,
        'red':total_red,
        'yellow':total_yellow,
        'green':total_green,
        'names':names,
        'screenshots':screenshots
    }