from customtkinter import *
from logic import *
from PIL import Image as img

set_default_color_theme("dark-blue")
set_appearance_mode("dark")


class App(CTk):
    def __init__(self):
        super().__init__()

        self.W = int(self.winfo_screenwidth() * 0.90)
        self.H = int(self.winfo_screenheight() * 0.90)

        self.title("Security Vision System")
        self.geometry(f"{self.W}x{self.H}")

        self.yolo_mode = False
        self.camera_running = False
        self.Face_detection = False
        self.detect_threat = False
        self.report = False

        self.view = Camera()

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=5)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=3)     
        self.grid_rowconfigure(1, weight=1) 

        self.command_row = 0

        #left side bar
        
        self.frame_1 = CTkFrame(master=self, fg_color="#1e1e1e", border_width=2,border_color="#555555")
        self.frame_1.grid(row=0, column=0, padx=10, pady=10, sticky="nswe",rowspan=3)

        self.frame_1.grid_propagate(False)

        self.frame_1.columnconfigure(0, weight=1)
        self.label_1 = CTkLabel(master=self.frame_1, text="Side bar", fg_color="transparent", font=("Arial",20), text_color="gray")
        self.label_1.grid(row=0, column=0, padx=10, pady=10)

        self.divider_1 = CTkFrame(master=self.frame_1, height=3, fg_color="#555555")
        self.divider_1.grid(row=1, column=0, sticky="ew", padx=0, pady=(0,10))

        #camera screen on the middle
        self.frame_2 = CTkFrame(master=self, fg_color="#000000", border_width=2, border_color="#555555")
        self.frame_2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.frame_2.grid_propagate(False)

        self.video_label =CTkLabel(master=self.frame_2,text="")
        self.video_label.grid(row=0,column=0, padx=0,pady=0,sticky="news")



        #right side bar
        self.frame_3 = CTkFrame(master=self, fg_color="#1e1e1e", border_width=2, border_color="#555555")
        self.frame_3.grid(row=0, column=2, padx=10, pady=10, sticky="nsew",rowspan=3)
        self.frame_3.grid_propagate(False)

        self.frame_3.columnconfigure(0, weight=1)

        self.label_3 = CTkLabel(master=self.frame_3, text="Logs", fg_color="transparent", font=("Arial",20), text_color="gray")
        self.label_3.grid(row=0, column=0, padx=10, pady=10)
        self.divider_3 = CTkFrame(master=self.frame_3, height=3, fg_color="#555555")
        self.divider_3.grid(row=1, column=0, sticky="ew", padx=0, pady=(0,10))

        #bottom bar---------------------------------------------------------------------#
        self.frame_4 = CTkFrame(master=self, fg_color="#323232", border_width=2, border_color="#555555")
        self.frame_4.grid(row=1, column=1, padx=10, pady=10, sticky="news")
        self.frame_4.grid_propagate(False)
        self.frame_4.columnconfigure(0, weight=1)
        self.frame_4.rowconfigure(0, weight=1)
        self.frame_4.columnconfigure(1,weight=1)
        self.frame_4.rowconfigure(1, weight=1)
        self.frame_4.rowconfigure(2, weight=1)
        self.frame_4.rowconfigure(4, weight=1)
        self.frame_4.columnconfigure(2, weight=1)
        


        self.frame_1.rowconfigure(2, weight=1)

        self.frame_3.rowconfigure(2, weight=1)

        ##command hostory--------------------->

        self.command_history = CTkTextbox(
            master=self.frame_1,
            fg_color="#181818",
            text_color="white",
            wrap="word",
            corner_radius=6
        )

        self.command_history.grid(row=2, column=0, padx=10,pady=10, sticky="news")
        self.command_history.configure(state="disabled")

        ##command entering box--------------------------->

        self.command_enter = CTkEntry(
            master= self.frame_1,
            placeholder_text="Enter command mater..."

        )

        self.command_enter.grid(
            row=3,
            column=0,
            padx=10,
            pady=10,
            sticky="we"
        )
        self.command_enter.bind("<Return>", self.handle_command)

        ##record display-------------------------->
        self.log_display =  CTkTextbox(
            master = self.frame_3,
            fg_color="#181818",
            text_color="white",
            wrap="none",
            corner_radius=6
        )
        self.log_display.grid(row=2, column=0, padx=10,pady=10, sticky="news")
        self.log_display.configure(state="disabled")




        ##live camera feed button----------------------------------------------------------#
        self.button = CTkButton(master=self.frame_4, text="◀ Start Live Cam", width=50,height=50,hover=False,
                                fg_color="blue", text_color="silver", 
                                command=self.toggle)
        self.button.grid(row=1,column=1, padx=10,pady=20)

        ##yolo button-------------------------------->
        self.button_yolo = CTkButton(master=self.frame_4,
                                text = "Detect Things Using YOLO",
                                fg_color="green",
                                text_color="silver",
                                width=50,
                                height=50,
                                command=self.toggle_yolo,
                                hover= False
                                )
        self.button_yolo.grid(row=0,column=0,padx=10,pady=10)

        ##DNN face detection-------------------------------------------------------->

        self.button_DNN = CTkButton(master=self.frame_4,
                                    text="Turn on Face Detection",
                                    fg_color="green",
                                    text_color="silver",
                                    width=50,
                                    height=50,
                                    command=self.toggle_face_detection,
                                    hover=False
                                    )
        
        self.button_DNN.grid(row=0,column=2, padx=10,pady=10)

        ##threat detection button----------------------------------------------------->

        self.button_threat_detection = CTkButton(
            master = self.frame_4,
            text = "Detect Threat",
            fg_color = "green",
            text_color="silver",
            width=50,
            height=50,
            command=self.toggle_threat_detection,
            hover=False
        )
        self.button_threat_detection.grid(row=2, column=0, padx=10,pady=10)

        ##file report button------------------------------------->

        self.button_report = CTkButton(
            master = self.frame_4,
            text = "Generate Report",
            fg_color = "green",
            text_color="silver",
            width=50,
            height=50,
            command=self.toggle_report,
            hover=False
        )

        self.button_report.grid(row=2, column= 2, padx=10,pady=10)


        ##select all on button ---------------->
        self.button_select_all = CTkButton(master=self.frame_4,
                                text = "Turn on EVERYTHING",
                                fg_color="black",
                                text_color="silver",
                                width=50,
                                height=50,
                                command=self.toggle_all_on,
                                hover= True, border_color="white", 
                                corner_radius=120, 
                                border_width=1
        )
        self.button_select_all.grid(row=4, column=0,padx=10,pady=20)
        
        ##Select all off button---------------------->
        self.button_select_off = CTkButton(master=self.frame_4,
                                text = "Turn off EVERYTHING",
                                fg_color="black",
                                text_color="silver",
                                width=50,
                                height=50,
                                command=self.toggle_all_off,
                                hover= True, border_color="white", 
                                corner_radius=120, 
                                border_width=1
        )
        self.button_select_off.grid(row=4, column=2,padx=10,pady=20)
        
        




        
    def toggle(self):
        self.camera_running = not self.camera_running

        if not self.camera_running:
            self.view.stopped()
            self.video_label.configure(image="")
            self.video_label.image = None
        else:
            self.camera()

        self.update_button()

    def toggle_yolo(self):

        self.yolo_mode = not self.yolo_mode
        self.update_button()

    def toggle_face_detection(self):
        self.Face_detection = not self.Face_detection
        self.update_button()
    
    def toggle_threat_detection(self):
        self.detect_threat = not self.detect_threat
        self.yolo_mode = True
        self.Face_detection = True
        self.update_button()
        
    def toggle_report(self):
        self.report = not self.report
        
        self.update_button()

        if self.report:
            self.report_access()
        

    def toggle_all_off(self):
        self.camera_running = False
        self.yolo_mode = False
        self.Face_detection = False
        self.detect_threat = False
        self.view.stopped()
        self.video_label.configure(image="")
        self.video_label.image = None
        self.update_button()
    
    def toggle_all_on(self):
        was_running = self.camera_running
        self.camera_running = True
        self.yolo_mode = True
        self.Face_detection = True
        self.detect_threat = True
        self.update_button()

        if not was_running:
            self.camera()
    
    
    def handle_command(self, event):
        cmd = self.command_enter.get()

        result = self.view.execute_command(cmd)

        self.add_command(cmd)

        if result == "__CLEAR__":
            self.clear_history()
        elif result == "__ATTEND__":
            self.record_history()
        elif result =="__CLEAR_LOGS__":
            self.clear_logs()
        elif result == "__THREAT_TIME__":
            self.dangerous_times()
        elif result == "__DATABASE__":
            self.sql_database_logs()

        
        else:
            self.ternimal_comment(result)
        
        self.command_enter.delete(0, "end")

    def clear_history(self):
        self.command_history.configure(state="normal")
        self.command_history.delete("1.0", "end")
        self.command_history.configure(state="disabled")

    def add_command(self, text):
        self.command_history.configure(state="normal")
        self.command_history.insert("end", "> "+text+"\n")
        self.command_history.see("end")
        self.command_history.configure(state="disabled")
    
    def ternimal_comment(self, text):
        self.command_history.configure(state="normal")
        self.command_history.insert("end", "~~ "+text+"\n")
        self.command_history.see("end")
        self.command_history.configure(state="disabled")
    
    def record_history(self):
        text_box = self.view.get_record()

        self.log_display.configure(state="normal")
        self.log_display.insert("end",text=text_box)
        self.log_display.see("end")
        self.log_display.configure(state="disabled") 
    
    def dangerous_times(self):

        text = self.view.danger_time()

        self.log_display.configure(state="normal")
        self.log_display.insert("end",text=text)
        self.log_display.see("end")
        self.log_display.configure(state="disabled") 

    def sql_database_logs(self):

        text = self.view.sql_database()

        self.log_display.configure(state="normal")
        self.log_display.insert("end",text=text)
        self.log_display.see("end")
        self.log_display.configure(state="disabled") 


        


    def clear_logs(self):
        self.log_display.configure(state="normal")
        self.log_display.delete("1.0", "end")
        self.log_display.configure(state="disabled")
    
    def report_access(self):
        get_report = self.view.report()

        self.log_display.configure(state="normal")
        self.log_display.insert("end",text=get_report)
        self.log_display.see("end")
        self.log_display.configure(state="disabled") 



    


    def update_button(self):
        ##camera Button
        if self.camera_running:
            self.button.configure(text="⏸ Stop Live Cam", fg_color="red")
        else:
            self.button.configure(text="▶ Start Live Cam", fg_color="blue")
        

        #yolo button
        if self.yolo_mode:
            self.button_yolo.configure(text="Stop Tracking With YOLO", fg_color="red")
        else:
            self.button_yolo.configure(text="Detect Things Using YOLO", fg_color="green")
        
        if self.Face_detection:
            self.button_DNN.configure(text="Turn off Face Detection", fg_color="red")
        else:
            self.button_DNN.configure(text="Turn on Face Detection", fg_color="green")
        
        if self.detect_threat:
            self.button_threat_detection.configure(fg_color="red")
        else:
            self.button_threat_detection.configure(fg_color="green")
        
        if self.report:
            self.button_report.configure(fg_color="red")
        else:
            self.button_report.configure(fg_color="green")




    def camera(self): ##actual camera displaying and stuff in here to go into the monitor

        if not self.camera_running:
            return
        
        
        frame = self.view.start_video()
        boxes = None

        if self.yolo_mode:
            frame, boxes = self.view.detection(frame)
        
        if self.Face_detection or self.detect_threat:
            frame = self.view.face_detection(frame)
        
        if self.detect_threat:
            if self.view.face_crop is not None:
                frame = self.view.detect_threats(frame, boxes)
        
        image = img.fromarray(frame)
        
        self.video = CTkImage(light_image=image, dark_image=image,
                            size=(int(self.frame_2.winfo_width()),int(self.frame_2.winfo_height()))
                            )
        self.video_label.configure(image=self.video)
        self.video_label.image = self.video
        
        self.after(40,self.camera)
    
    