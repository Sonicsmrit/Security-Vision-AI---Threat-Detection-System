import cv2 as cv
from ultralytics import YOLO
import numpy as np
from database import *
from deepface import DeepFace
from fpdf import FPDF
import os
import time
import pygame

class Camera:
    def __init__(self):
        self.video = None
        self.model = YOLO("DNN/yolo26n.pt")
        self.to_detect = {
            'person':0,
            'phone': 67,
            'knife': 43,
            'bat': 34
        }
        self.proto_text = "DNN/deploy.prototxt"
        self.nuro = "DNN/res10_300x300_ssd_iter_140000.caffemodel"
        self.DNN = cv.dnn.readNetFromCaffe(self.proto_text, self.nuro)
        
        self.face_crop = None
        self.user_enter = False
        self.password = "o123"
        self.face_authority = False

        with open("Data Files/index.txt", "r") as f:
            self.index = int(f.read().strip())

        self.real_name = "Unknown"
        self.x1=0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.confidence = 0
        self.capt = 0
        self.last_difference = float("inf")

        pygame.mixer.init()
        pygame.mixer.music.load("mixkit-classic-alarm-995.wav")
    
    def start_video(self):

        if self.video is None or not self.video.isOpened():
            self.video = cv.VideoCapture(0)
        _, frame = self.video.read()
        frame = cv.flip(frame, 1)
        

        frame = cv.cvtColor(frame,cv.COLOR_BGR2RGB)

        return frame
    
    def stopped(self):
        self.video.release()

        
    def detection(self, frame_input):
        
        frame = frame_input
        detect = self.model(frame, classes=[self.to_detect['bat'],
                                            self.to_detect['phone'],
                                            self.to_detect['knife'],
                                            self.to_detect['bat'],
                                            self.to_detect['person']],
                                            verbose=False, conf=0.4)
        boxes = detect[0].boxes
        plotted = detect[0].plot()
        

        return plotted, boxes
    
    def face_detection(self, frame_input):
        frame = frame_input
        h,w = frame.shape[:2]
        blob = cv.dnn.blobFromImage(image=frame, scalefactor= 1, size=(300,300), mean=(104, 177, 123))

        self.DNN.setInput(blob)

        detect = self.DNN.forward()

        for i in range(detect.shape[2]):
            confidence = detect[0,0,i,2]
            self.confidence = confidence

            if confidence >0.7:
                box = detect[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                cv.rectangle(frame, (startX, startY), (endX, endY), (255, 0, 0), 2)

                self.face_crop = frame[startY:endY, startX:endX]
                self.x1 = startX
                self.y1 = startY
                self.x2 = endX
                self.y2 = endY


        return frame
        
    def execute_command(self, cmd):

        if not self.user_enter:
            if cmd == "/enter-user":
                self.user_enter = not self.user_enter
                return "Enter password Master"
        
        elif self.user_enter:
            if cmd == self.password:
                self.user_enter = not self.user_enter
                self.face_authority = not self.face_authority
                return "Enter the users name Master, also ensure that they are in Frame and the face can be detected."
            else:
                self.user_enter = not self.user_enter
                return "Thats not the password, Master"

            
        if self.face_authority:
            self.face_authority = not self.face_authority
            username = cmd

            database(self.face_crop, username=username)

            return "User Successfully added, Master"

        if cmd == "/clear":
            return "__CLEAR__"

        if cmd == "/help":
            return """command: /enter-user
            - Enter new user to the system
            
            command: /clear
            -clears chat history screen
            
            -command: /attendence
            -list of known people the camera has seen
            
            -command: /clear-logs
            -clears the log screen
            
            -command: /threat-time
            -shows you the times when a threat was detected
            
            -command:/database
            -shows everything thats in your SQL database"""
        
        if cmd == "/attendence":
            return "__ATTEND__"
        
        if cmd == "/clear-logs":
            return "__CLEAR_LOGS__"
        
        if cmd == "/threat-time":
            return "__THREAT_TIME__"
        
        if cmd == "/database":
            return "__DATABASE__"

        
        return "unknown command Master"



        
    def detect_threats(self, frame_input, boxes = None):
        frame = frame_input
        data_dict = load_database()

        if boxes is None:
            detect = self.model(frame, classes=[self.to_detect['bat'], self.to_detect['knife'], self.to_detect['person'], self.to_detect['phone']], conf=0.25, verbose=False)
            boxee = detect[0].boxes
        else:
            boxee = boxes

        
        smallest_distance = float("inf")
        Threshold_val = 15

        self.capt += 1

        if self.capt%40 == 0:
            if self.face_crop is None or self.face_crop.size == 0:
                return frame
            
            face_crop_small = cv.resize(self.face_crop, (100,100))

            try:
                current_embedding = DeepFace.represent(
                    img_path=face_crop_small,
                    model_name="Facenet",
                    enforce_detection=False
                )
                previous_embedding = current_embedding
            except:
                current_embedding = previous_embedding

            
            ##loop to compare all the data from the database and the current face data
            for name, stored_embedding in data_dict.items():
                #finding the difference between the current face and the face in the database
                difference = np.linalg.norm(np.array(current_embedding[0]["embedding"]) - np.array(stored_embedding))

                #putting the smallest difference in the smallest_distance to see if there is a match
                if difference < smallest_distance:
                    smallest_distance = difference
                    self.real_name = name
                    self.last_difference = smallest_distance ##keeping it in the last_diff variable so the data doesnt flicker
        


        # Check if weapon detected first
        weapon_detected = False
        weapon_name = None
    
        if boxee is not None and boxee.cls is not None and len(boxee.cls) > 0:
            classes = boxee.cls
            for cls_id in classes:
                cls_id_int = int(cls_id.item())
                for key, value in self.to_detect.items():
                    if value == cls_id_int and key in ['phone','bat','knife']:  # Only actual weapons
                        weapon_detected = True
                        weapon_name = key
                        break

        # Now determine threat based on person + weapon
        if self.last_difference < Threshold_val:  # KNOWN PERSON
            cv.rectangle(frame, (self.x1,self.y1), (self.x2,self.y2), (0,255,0), 3)
            cv.putText(frame, f"{self.real_name}", (self.x1, self.y1-10), cv.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 3)
            threat("GREEN", f"{self.real_name}", weapon_name, float(self.confidence), str(None))
            record(self.real_name)

        else:  # UNKNOWN PERSON
            if weapon_detected:  # Unknown + Weapon = RED
                cv.rectangle(frame, (self.x1,self.y1), (self.x2,self.y2), (255,0,0), 3)
                cv.putText(frame, "Warning!", (0, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 3)
                cv.putText(frame, "!!!Dangerous USER!!!", (self.x1, self.y1-10), cv.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 3)


                
                bgr_frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)
                cv.imwrite(f"images/img{self.index:03d}.jpg", bgr_frame)

                self.index += 1

                with open("Data Files/index.txt", "w") as f:
                    f.write(str(self.index))

                
                current_time = datetime.now()
                formatted_time = current_time.strftime("%I:%M %p")
                formatted_date = current_time.strftime("%Y-%m-%d")

                
                threat("RED", "Dangerous USER", weapon_name, float(self.confidence), f"images/img{index:03d}.jpg")

                with open("Data Files/danger_time.txt", 'r') as f:
                    last_time = f.readlines()[-1].strip()

                    if last_time != f"{formatted_time} {formatted_date}":

                
                        with open("Data Files/danger_time.txt", 'a') as f:
                            f.write(str(formatted_time + " " + formatted_date + "\n"))
                
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play()
                
                
            
            else:  # Unknown + No weapon = YELLOW
                cv.rectangle(frame, (self.x1,self.y1), (self.x2,self.y2), (255,255,0), 3)
                cv.putText(frame, "Unknown User", (self.x1, self.y1-10), cv.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 3)
                threat("YELLOW", "Unknown USER", str(None), float(self.confidence), str(None))
    
        return frame
    
    def get_record(self):
        box = []

        with open("Data Files/record.csv", "r") as f:
            read = csv.DictReader(f)
            box.append("\n\n")
            box.append("Record Of Known People Who Were Seen On Cam\n")
            box.append("-"*90 + "\n")
            box.append(f"|{'Name':^15}||{'Date':^15}||{'Time':^15}||{'Status':^15}|\n")
            for apt in read:
                box.append("-"*90 + "\n")
                box.append(f"|{apt['Name']:^15}||{apt['Date']:^15}||{apt['Time']:^15}||{apt['Status']:^15}|\n")

            box.append("-"*90 + "\n")
        result = "".join(box)
        return result


    def danger_time(self):
        value = []
        with open("Data Files/danger_time.txt", 'r') as f:
            value.append("\n\nThreat Detected Time And Date\n\n")
            time_date = f.read()
            value.append(time_date)

        result = "".join(value)
        
        return result

    def sql_database(self):
        rows = get_database()

        def clean(val):
            if val is None:
                return "N/A"
            if isinstance(val, float):
                return f"{val:.2f}"
            return str(val)
        
        values = []

        values.append("-"*300 + "\n")

        values.append(f"|{'ID':^25}||{'TimeStamp':^25}||{'Date':^25}||{'Threat Level':^25}||{'Person Name':^25}||{'Weapon Detected':^25}||{'Confidence':^25}||{'Screenshot Path':^25}|\n")

        for row in rows:
            values.append("-"*300 + "\n")
            values.append(f"|{clean(row[0]):^25}||{clean(row[1]):^25}||{clean(row[2]):^25}||{clean(row[3]):^25}||{clean(row[4]):^25}||{clean(row[5]):^25}||{clean(row[6]):^25}||{clean(row[7]):^25}|\n")

        values.append("-"*300 + "\n")

        result = "".join(values)

        return result


    def report(self):
        
        current_time = datetime.now()
        formatted_date = current_time.strftime("%Y-%m-%d")

        dashbd = dashboard(formatted_date)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Times", size=12)
        pdf.cell(200, 10, text="Daily Security Report", ln=True)
        pdf.cell(200, 10, text=f"Total Alerts: {dashbd['total']}", ln=True)
        pdf.cell(200,10, text=f"Total Red Alerts:{dashbd['red']}", ln=True)
        pdf.cell(200,10, text=f"Total Yellow Alerts:{dashbd['yellow']}", ln=True)
        pdf.cell(200,10, text=f"Total Green Alerts:{dashbd['green']}", ln=True)
        pdf.cell(200,10, text=f"Names", ln=True)


        for name in dashbd['names']:
            name = name[0]
            pdf.cell(200,10, text=f"{name}", ln=True)

        pdf.cell(200,10, text=f"Screenshots", ln=True)
        for shots in dashbd['screenshots']:
            screenshot_path = shots[0] 

            if screenshot_path and os.path.exists(screenshot_path): 
                pdf.add_page()
                pdf.image(screenshot_path, x=10, y=10, w=pdf.w - 20)
                    

        pdf.output(f"Report/report{formatted_date}.pdf")
    
        return f"PDF made in: Report/report{formatted_date}.pdf\n"
                
                






