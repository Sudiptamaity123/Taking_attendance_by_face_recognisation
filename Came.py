from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen,ScreenManager
from kivymd.uix.textfield.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivy.uix.recycleview import RecycleView

from imutils.video import VideoStream
from imutils.video import FPS
from imutils import paths
import face_recognition
import imutils
import pickle
import time
import cv2
import os
import datetime

screen_helper = """
ScreenManager:
        MenuScreen:
        RecognitionScreen:
        RegistrationScreen:
        AttendanceScreen:

<RV>:
        viewclass: 'MDRectangleFlatButton'
        orientation: "vertical"
        spacing: 40
        padding:10, 10
        RecycleBoxLayout:
                color:(0, 0.7, 0.4, 0.8)
                default_size: None, dp(100)

                # defines the size of the widget in reference to width and height
                default_size_hint: 1, None 
                size_hint_y: None
                size_hint_x: 
                height: self.minimum_height
                orientation: 'vertical' # defines the orientation of data items
        
<MenuScreen>
        name: 'Menu'
        MDRectangleFlatButton:
                text: 'Recognition'
                pos_hint: {'center_x':0.5,'center_y':0.7}
                on_press:
                        root.manager.current = 'Recognition'
                        root.manager.transition.direction = "left"
                        
        MDRectangleFlatButton:
                text: 'Registration'
                pos_hint: {'center_x':0.5,'center_y':0.6}
                on_press:
                        root.manager.current = 'Registration'
                        root.manager.transition.direction = "left"
                        
        MDRectangleFlatButton:
                text: 'Attendance'
                pos_hint: {'center_x':0.5,'center_y':0.5}
                on_press:
                        root.manager.current = 'Attendance'
                        root.manager.transition.direction = "left"
                        
        MDRectangleFlatButton:
                text: 'Quit'
                pos_hint: {'center_x':0.5,'center_y':0.4}
                on_press: app.stop()

<RecognitionScreen>
        name: 'Recognition'
        MDRectangleFlatButton:
                text: 'Start Recognition'
                pos_hint: {'center_x':0.5,'center_y':0.5}
                on_press: root.Face_rec()
        MDRectangleFlatButton:
                text: 'Back'
                pos_hint: {'center_x':0.5,'center_y':0.4}
                on_press:
                        root.manager.current = 'Menu'
                        root.manager.transition.direction = "right"
                
<RegistrationScreen>
        name: 'Registration'
        namefield1: namefield1
        
        MDTextField:
                id: namefield1
                hint_text: "Roll Number_Name"
                helper_text: "Ex : 18700120058_Saurjya"
                pos_hint: {'center_x':0.5,'center_y':0.7}
                size_hint_x:None
                width:300
                helper_text_mode: "on_focus"
                
        MDRectangleFlatButton:
                text: 'Take a Pic'
                pos_hint: {'center_x':0.5,'center_y':0.6}
                on_press: root.Take_a_pic()
                
        MDRectangleFlatButton:
                text: 'Register'
                pos_hint: {'center_x':0.5,'center_y':0.5}
                on_press: root.registerr()
                
        MDRectangleFlatButton:
                text: 'Back'
                pos_hint: {'center_x':0.5,'center_y':0.4}
                on_press:
                        root.manager.current = 'Menu'
                        root.manager.transition.direction = "right"
                
<AttendanceScreen>
        name: 'Attendance'
        BoxLayout:
                orientation: "vertical"
                RV:
                MDRectangleFlatButton:
                        text: 'Back'
                        pos_hint: {'center_x':0.5,'center_y':0.4}
                        on_press:
                                root.manager.current = 'Menu'
                                root.manager.transition.direction = "right" 
"""
class MenuScreen(Screen):               
        pass

class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        x=[]
        today = datetime.datetime.now()
        filename ="Attendance_"+ today.strftime("%d_")+today.strftime("%m_")+today.strftime("%G")+".txt"
        try:
                f = open('%s' % filename, "r")
                x = f.readlines()
        except:
                x.append("No File found")
                x.append("Please Do Recognition Attendance ")
                x.append("After attendance Rerun The app to see changes ")
        self.data = [{'text': str(i)} for i in x]
        try:
                f.close()
        except:
                pass

class AttendanceScreen(Screen):
        pass

class RegistrationScreen(Screen):
        def registerr(self):
                print("[INFO] start processing faces...")
                imagePaths = list(paths.list_images("dataset"))

                knownEncodings = []
                knownNames = []

                for (i, imagePath) in enumerate(imagePaths):
                        print("[INFO] processing image {}/{}".format(i + 1,
                                len(imagePaths)))
                        name = imagePath.split(os.path.sep)[-2]

                        image = cv2.imread(imagePath)
                        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                        
                        boxes = face_recognition.face_locations(rgb,
                                model="hog")

                        encodings = face_recognition.face_encodings(rgb, boxes)

                        for encoding in encodings:
                                
                                knownEncodings.append(encoding)
                                knownNames.append(name)

                print("[INFO] serializing encodings...")
                data = {"encodings": knownEncodings, "names": knownNames}
                f = open("encodings.pickle", "wb")
                f.write(pickle.dumps(data))
                f.close() 
        def Take_a_pic(self):

                namefield1 = ObjectProperty(None)
                print("Your name is",self.namefield1.text)
                name = self.namefield1.text
                path = os.getcwd()+'/dataset/'+name
                print (path)
                cam = cv2.VideoCapture(0)
                try: 
                    os.makedirs(path) 
                except OSError as error: 
                    print(error) 

                cv2.namedWindow("press space to take a photo", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("press space to take a photo", 500, 300)

                img_counter = 0

                while True:
                    ret, frame = cam.read()
                    if not ret:
                        print("failed to grab frame")
                        break
                    cv2.imshow("press space to take a photo", frame)

                    k = cv2.waitKey(1)
                    if k%256 == 27:
                        # ESC pressed
                        print("Escape hit, closing...")
                        break
                    elif k%256 == 32:
                        # SPACE pressed
                        img_name = "dataset/"+ name +"/image_{}.jpg".format(img_counter)
                        cv2.imwrite(img_name, frame)
                        print("{} written!".format(img_name))
                        img_counter += 1

                cam.release()

                cv2.destroyAllWindows()
                self.namefield1.text = ""
        pass

class RecognitionScreen(Screen):
        def Face_rec(self):
                currentname = "unknown"
                encodingsP = "encodings.pickle"
                today = datetime.datetime.now()
                print("[INFO] loading encodings + face detector...")
                data = pickle.loads(open(encodingsP, "rb").read())
                filename ="Attendance_"+ today.strftime("%d_")+today.strftime("%m_")+today.strftime("%G")+".txt"
                vs = VideoStream(src=0,framerate=10).start()
                time.sleep(2.0)
                attendance = {}
                f = open('%s' % filename, "w")

                while True:
                        frame = vs.read()
                        frame = imutils.resize(frame, width=500)
                        boxes = face_recognition.face_locations(frame)
                        encodings = face_recognition.face_encodings(frame, boxes)
                        names = []

                        for encoding in encodings:
                                
                                matches = face_recognition.compare_faces(data["encodings"],
                                        encoding)
                                name = "Unknown" 

                                
                                if True in matches:
                                      
                                        matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                                        counts = {}

                                      
                                        for i in matchedIdxs:
                                                name = data["names"][i]
                                                counts[name] = counts.get(name, 0) + 1

                                        
                                        name = max(counts, key=counts.get)

                                        
                                        if currentname != name:
                                                currentname = name
                                                now = datetime.datetime.now()
                                                dateStr = now.strftime("%Y-%m-%d %H:%M:%S")
                                                timer = f" Date and time : {dateStr}\n"
                                                if currentname not in attendance:
                                                        attendance[currentname] = timer
                                                print(currentname)

                              
                                names.append(name)


                        for ((top, right, bottom, left), name) in zip(boxes, names):
                                
                                cv2.rectangle(frame, (left, top), (right, bottom),
                                        (0, 255, 225), 2)
                                y = top - 15 if top - 15 > 15 else top + 15
                                cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                                        .8, (0, 255, 255), 2)

                       
                        cv2.imshow("Facial Recognition is Running Press q to Quit", frame)
                        key = cv2.waitKey(1) & 0xFF

                       
                        if key == ord("q"):
                                for key, value in attendance.items():
                                        f.write('%s :%s' % (key, value))
                                #print(attendance)
                                break
  
                cv2.destroyAllWindows()
                vs.stop()
                f.close()
        pass

sm = ScreenManager()
sm.add_widget(MenuScreen(name = 'Menu'))
sm.add_widget(RecognitionScreen(name = 'Recognition'))
sm.add_widget(RegistrationScreen(name = 'Registration'))
sm.add_widget(AttendanceScreen(name = 'Attendance'))

class FaceAttendanceApp(MDApp):
        def Face_rec(self):
            print("Hello")

        def build(self):
                self.theme_cls.theme_style = "Dark"
                self.theme_cls.primary_palette = "Blue"
                screen = Builder.load_string(screen_helper)
                return screen

FaceAttendanceApp().run()
