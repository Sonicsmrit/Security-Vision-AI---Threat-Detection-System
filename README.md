# Security Vision AI - Threat Detection System

A real-time AI-powered security monitoring system built with Python. Combines **face recognition**, **weapon detection via YOLO**, and a **live threat alert dashboard** — all inside a professional customtkinter GUI.

---

## What It Does

| Feature | Description |
|---|---|
| Live Camera Feed | Real-time webcam stream displayed in the GUI |
| Face Recognition | Identifies known vs unknown people using DeepFace (Facenet embeddings) |
| Weapon Detection | Detects knives, bats, and phones using a custom YOLOv8 model |
| Threat Levels | GREEN (known person), YELLOW (unknown, no weapon), RED (unknown + weapon) |
| Auto Screenshots | Saves timestamped images when a RED threat is detected |
| SQLite Logging | Every detection event is logged to a local database |
| Attendance Record | Tracks when known people were seen on camera (CSV) |
| PDF Reports | Generates a daily security report with stats and screenshots |
| Terminal Interface | Built-in command panel for managing users and viewing logs |

---

## Project Structure

```
│
├── main.py                   #runs the whole system
├── ui.py                     # GUI entry point (customtkinter)
├── logic.py                  # Camera, detection, and command logic
├── database.py               # Face DB, SQLite, attendance, and reporting helpers
│
├── DNN/
│   ├── yolo26n.pt            # Custom YOLO model weights
│   ├── deploy.prototxt       # DNN face detector config
│   └── res10_300x300_ssd_iter_140000.caffemodel
│
├── Data Files/
│   ├── face_db.pkl           # Pickle database of known face embeddings
│   ├── record.csv            # Attendance log
│   ├── danger_time.txt       # Log of RED alert timestamps
│   └── index.txt             # Screenshot counter
│
├── images/                   # Auto-saved threat screenshots
│   └── img001.jpg ...
│
└── Report/                   # Generated PDF reports
    └── report2025-01-01.pdf ...
```

---

### 5. Run

```bash
python main.py
```

---

## Requirements

```
opencv-python
ultralytics
deepface
customtkinter
Pillow
fpdf2
numpy
pygame

```

---

## GUI Overview

```
┌──────────────────┬──────────────────────────┬──────────────────┐
│   Terminal       │                          │   Logs           │
│                  │     Live Camera Feed     │                  │
│  Command history │                          │  Detection logs  │
│  > /help         │                          │  Attendance      │
│  > /attendence   │                          │  DB output       │
│                  │                          │                  │
│  [command entry] │                          │                  │
├──────────────────┼──────────────────────────┤                  │
│                  │  [YOLO] [Start Cam] [Face]│                 │
│                  │  [Threat]     [Report]   │                  │
│                  │  [All ON]     [All OFF]  │                  │
└──────────────────┴──────────────────────────┴──────────────────┘
```

---

## Terminal Commands

| Command | Description |
|---|---|
| `/enter-user` | Register a new face into the system (prompts for password then name) |
| `/attendence` | Display attendance log of known people seen on camera |
| `/threat-time` | Show timestamps of all RED threat detections |
| `/database` | View the full SQLite threat log |
| `/clear` | Clear the terminal command history |
| `/clear-logs` | Clear the log display panel |
| `/help` | List all available commands |

> **Default password:** `o123`  
> Change it by editing `self.password` in `logic.py`

---

## Threat Level System

| Level | Condition |
|---|---|
| GREEN | Known person identified |
| YELLOW | Unknown person, no weapon detected |
| RED | Unknown person with weapon detected |

When RED is triggered:
- A screenshot is saved to `images/`
- The event is logged to the SQLite database
- The timestamp is recorded in `danger_time.txt`

---

## How Face Recognition Works

1. **Register a face** — use `/enter-user` in the terminal while the person is visible in the camera. The system crops the detected face and extracts a 128-dimensional Facenet embedding via DeepFace, storing it in `face_db.pkl`.

2. **Live identification** — every 40 frames, the system compares the current face embedding against all stored embeddings using Euclidean distance.

3. **Match threshold** — a distance below `15` is considered a match. Adjust `Threshold_val` in `logic.py` to tune sensitivity.

---

## Generating a Report

Click **Generate Report** in the GUI or handle it programmatically. The PDF report includes:

- Date and total alert counts (RED / YELLOW / GREEN)
- List of known persons detected that day
- All threat screenshots embedded in the document

Reports are saved to `Security Vision with UI/Report/report<date>.pdf`.

---

## Configuration

| Setting | Location | Default |
|---|---|---|
| Admin password | `logic.py` → `self.password` | `o123` |
| Face match threshold | `logic.py` → `Threshold_val` | `15` |
| Face detection confidence | `logic.py` → `face_detection()` | `0.7` |
| YOLO detection confidence | `logic.py` → `detection()` | `0.4` |
| Re-identification interval | `logic.py` → `self.capt % 40` | Every 40 frames |
| Weapon classes | `logic.py` → `self.to_detect` | person, phone, knife, bat |


---


## License

MIT License — free to use, modify, and distribute.