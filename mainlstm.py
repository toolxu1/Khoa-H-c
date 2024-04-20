from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.uic import loadUi
import cv2
import sys
import imagiz
import speech_recognition as sr
from moviepy.editor import  ImageSequenceClip
import mediapipe as mp
import pandas as pd
import numpy as np
import pickle
from win32com.client import Dispatch
import os
import socket
mp_drawing = mp.solutions.drawing_utils 
mp_holistic = mp.solutions.holistic
speak = Dispatch("SAPI.SpVoice").Speak
server=imagiz.Server()
host = '26.64.220.173'
port = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))
class SpeechToVideoThread(QThread):
    video = pyqtSignal(QImage)
    audioTextChanged = pyqtSignal(str)
    def __init__(self, img_dir, video_output_path):
        super(SpeechToVideoThread, self).__init__()
        self.img_dir = img_dir
        self.img_dir2 = r"D:\img2"
        self.video_output_path = video_output_path
        self.video_output_path2 = r"output_video2.mp4"
        self.audio_text = ""
        self.is_recording = False
    def run(self):
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300
        while self.is_recording:
            with sr.Microphone() as source:
                print("Recording...") #Bắt đầu nhận diện giọng nói
                audio = recognizer.listen(source)
            try:
                self.audio_text = recognizer.recognize_google(audio) #đây là kết quả mà mô hình trả về
                print("Ket qua: ", self.audio_text) 
                self.create_video_from_text()
                self.audioTextChanged.emit(self.audio_text)
            except sr.UnknownValueError:
                print("Er!")  #Bỏ qua nếu không thể nhận diện
            except sr.RequestError as e:
                print(f"Lỗi: {e}")
    def start_recording(self):
        self.is_recording = True #Em đánh dấu cho biến is_recording là đang hoạt động
        self.start() 

    def stop_recording(self):
        self.is_recording = False
        self.wait()
        
    # hàm thêm đường dẫn ảnh từ văn bản nhận diện được
    def create_video_from_text(self):
        img_list = []
        img_list2 = []
        for char in self.audio_text.lower():
            if char != ' ':
                img_path = os.path.join(self.img_dir, f"{char}.jpg").replace('\\', '/')
                if os.path.exists(img_path):
                    img_list.append(img_path)
            elif char == ' ':
                img_path = os.path.join(self.img_dir, 'space.jpg').replace('\\', '/')
                if os.path.exists(img_path):
                    img_list.append(img_path)
            else:
                continue
        for char in self.audio_text.lower():
            if char != ' ':
                img_path = os.path.join(self.img_dir2, f"{char}.jpg").replace('\\', '/')
                if os.path.exists(img_path):
                    img_list2.append(img_path)
            elif char == ' ':
                img_path = os.path.join(self.img_dir2, 'space.jpg').replace('\\', '/')
                if os.path.exists(img_path):
                    img_list2.append(img_path)
            else:
                continue
        print("Image List:", img_list)
        if img_list:
            self.show_video(img_list)
            self.show_video2(img_list2)
            self.audioTextChanged.emit("Video created!")
            print("Done")
    #tạo video bằng ảnh ngôn ngữ ký hiệu
    def show_video(self, img_list):
        frame_list = []
        for img_path in img_list:
            frame = cv2.imread(img_path)
            if frame is not None:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_list.append(rgb_image)

        if frame_list:
            fps = 0.25
            clip = ImageSequenceClip(frame_list, fps=fps)
            clip.write_videofile(self.video_output_path, codec='libx264', fps=fps)
    #tạo video bằng ảnh chữ cái thường
    def show_video2(self, img_list2):
        frame_list = []
        for img_path in img_list2:
            frame = cv2.imread(img_path)
            if frame is not None:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_list.append(rgb_image)

        if frame_list:
            fps = 0.25
            clip = ImageSequenceClip(frame_list, fps=fps)
            clip.write_videofile(self.video_output_path2, codec='libx264', fps=fps)
class Video(QThread):
    vid = pyqtSignal(QImage)
    def run(self):
        self.hilo_corriendo = True
        video_path = r"D:\a\output_video.mp4"
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)  # Get the frame rate
        delay = int(1000 / fps)  # Calculate delay between frames
        while self.hilo_corriendo:
            ret, frame = cap.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                p = convert_to_Qt_format.scaled(890, 440, Qt.KeepAspectRatio)
                self.vid.emit(p)
                
                self.msleep(delay)  # Introduce delay to match the frame rate
        cap.release()
    def stop(self):
        self.hilo_corriendo = False
        self.quit()
class Video2(QThread):
    vid2 = pyqtSignal(QImage)

    def run(self):
        self.check = True
        video_path = r"D:\a\output_video2.mp4"
        cap = cv2.VideoCapture(video_path)
        
        fps = cap.get(cv2.CAP_PROP_FPS) 
        delay = int(1000 / fps)
        
        while self.check:
            ret, frame = cap.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                p = convert_to_Qt_format.scaled(890, 440, Qt.KeepAspectRatio)
                self.vid2.emit(p)
                
                self.msleep(delay)  # Introduce delay to match the frame rate
        cap.release()

    def stop(self):
        self.check = False
        self.quit()
class Ham_Camera(QThread):
    luongPixMap1 = pyqtSignal(QImage)
    luongPixMap2 = pyqtSignal(QImage)
    luongString1 = pyqtSignal(str)
    luongString2 = pyqtSignal(str)
    luongClearSignal = pyqtSignal()

    def __init__(self):
        super(Ham_Camera, self).__init__()
        self.checkTrung = ""
        self.trangThai = True
        self.string = ""
        self.string2 = ""
        self.frame_count_threshold = 20  # Số frame tối thiểu để hiển thị classname
        self.current_frame_count = 0
        # Kết nối tín hiệu luongString1 của luồng camera với hàm update_string
        self.luongString1.connect(self.update_string1)
        self.luongString2.connect(self.update_string2)
        # Kết nối tín hiệu luongClearSignal của luồng camera với hàm clear_string
        self.luongClearSignal.connect(self.clear_string)

    def update_string1(self, new_string):
        self.string = new_string
    def update_string2(self, new_string):
        self.string2 = new_string
    def clear_string(self):
        # Xử lý khi nút "clear" được nhấn
        # Cập nhật giá trị của self.string thành chuỗi rỗng
        self.string = ""
    def run(self):
        # message_chat = client.recv(1024).decode('utf-8')
        with open('body_language.pkl', 'rb') as f:
            model = pickle.load(f)
        # server_ip = "26.23.20.235"
        # encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        # client = imagiz.Client("cc1", server_ip=server_ip)
        cap = cv2.VideoCapture(2) #khởi tạo webcam
        cap.set(380,380)
        # image_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        # image_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        x_ = []
        y_ = []
        
        with mp_holistic.Holistic(min_detection_confidence=0.2, min_tracking_confidence=0.2) as holistic:
            while self.trangThai:# chạy liên tục quá trình nhận diện
                ret, frame1 = cap.read() #đọc ảnh từ webcam
                message_cam=server.receive()
                frame2=cv2.imdecode(message_cam.image,1)
                H, W, _ = frame1.shape
                H2, W2, _ = frame2.shape
                if ret: #nếu như camera được khởi tạo thành công thì sẽ chạy phần xử lý, nếu không thì sẽ thoát chương trình
                    image1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
                    image1.flags.writeable = False
                    results1 = holistic.process(image1)
                    image1.flags.writeable = True
                    cv2.imwrite('shared_frame.jpg', image1)
                    image2 = frame2
                    image2.flags.writeable = False
                    results2 = holistic.process(image2)
                    image2.flags.writeable = True  
                    # cv2.imshow('r', image2)
                    mp_drawing.draw_landmarks(image1, results1.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                                 mp_drawing.DrawingSpec(color=(80,22,10), thickness=2, circle_radius=4),
                                 mp_drawing.DrawingSpec(color=(80,44,121), thickness=2, circle_radius=2)
                                )
                    # mp_drawing.draw_landmarks(image2, results2.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS, 
                    #              mp_drawing.DrawingSpec(color=(80,22,10), thickness=2, circle_radius=4),
                    #              mp_drawing.DrawingSpec(color=(80,44,121), thickness=2, circle_radius=2)
                    #             )
                    try:
                        rh1 = results1.right_hand_landmarks.landmark
                        rh_row1 = list(np.array([[landmark.x, landmark.y, landmark.z] for landmark in rh1]).flatten())
                        row1 = rh_row1
                        X1 = pd.DataFrame([row1])
                        body_language_class1 = model.predict(X1)[0]
                        body_language_prob1 = model.predict_proba(X1)[0]
                        if results1.right_hand_landmarks:
                            bbox1 = self.get_hand_bbox(results1.right_hand_landmarks, W, H)
                            cv2.rectangle(image1, bbox1[0], bbox1[1], (255, 255, 255), 2)
                            class_name1 = body_language_class1.split(' ')[0]
                            prob_text1 = f'{class_name1}: {round(body_language_prob1[np.argmax(body_language_prob1)], 2)}'
                            cv2.putText(image1, prob_text1, (bbox1[0][0], bbox1[0][1] - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)           
                        if body_language_prob1[np.argmax(body_language_prob1)] >= 0.85 and body_language_class1 != self.checkTrung:
                            if body_language_class1 == "space": 
                                self.string += " "
                                self.luongString1.emit(self.string)
                                self.checkTrung = body_language_class1
                            else:
                                self.string += body_language_class1
                                self.luongString1.emit(self.string)
                                self.checkTrung = body_language_class1
                        # image1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
                        # image1_rgb = cv2.cvtColor(image1, cv2.COLOR_BGR2RGB)
                        

                        # rh2 = results2.right_hand_landmarks.landmark
                        # rh_row2 = list(np.array([[landmark.x, landmark.y, landmark.z] for landmark in rh2]).flatten())
                        # row2 = rh_row2
                        # X2 = pd.DataFrame([row2])
                        # body_language_class2 = model.predict(X2)[0]
                        # body_language_prob2 = model.predict_proba(X2)[0]
                        # if results2.right_hand_landmarks:
                        #     bbox2 = self.get_hand_bbox(results2.right_hand_landmarks, W2, H2)
                        #     cv2.rectangle(image2, bbox2[0], bbox2[1], (255, 255, 255), 2)
                        #     class_name2 = body_language_class2.split(' ')[0]
                        #     prob_text2 = f'{class_name2}: {round(body_language_prob2[np.argmax(body_language_prob2)], 2)}'
                        #     cv2.putText(image2, prob_text2, (bbox2[0][0], bbox2[0][1] - 10),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                        # if body_language_prob2[np.argmax(body_language_prob2)] >= 0.85 and body_language_class2 != self.checkTrung2:
                        #     if body_language_class2 == "space":
                        #         self.string2 += " "
                        #         self.luongString2.emit(self.string2)
                        #         self.checkTrung2 = body_language_class2
                        #     else:
                        #         self.string2 += body_language_class2
                        #         self.luongString2.emit(self.string2)
                        #         self.checkTrung2 = body_language_class2
                    except:
                        pass
                    h, w, ch = image1.shape
                    bytes_per_line = ch * w
                    convert_to_Qt_format = QImage(image1.data, w, h, bytes_per_line, QImage.Format_RGB888)
                    p = convert_to_Qt_format.scaled(891, 461, Qt.KeepAspectRatio)
                    self.luongPixMap1.emit(p)

                    h2, w2, ch2 = image2.shape
                    bytes_per_line2 = ch2 * w2
                    convert_to_Qt_format2 = QImage(image2.data, w2, h2, bytes_per_line2, QImage.Format_RGB888)
                    p2 = convert_to_Qt_format2.scaled(891, 461, Qt.KeepAspectRatio)
                    self.luongPixMap2.emit(p2)
                else:
                    break
        cap.release()
    def stop(self): 
        self.trangThai = False
    def get_hand_bbox(self, landmarks, image_width, image_height):
        x_min, x_max, y_min, y_max = float('inf'), 0, float('inf'), 0

        for landmark in landmarks.landmark:
            x, y = int(landmark.x * image_width), int(landmark.y * image_height)
            x_min = min(x_min, x) - 3
            x_max = max(x_max, x) + 1
            y_min = min(y_min, y) - 3
            y_max = max(y_max, y) + 1

        bbox = ((x_min, y_min), (x_max, y_max))
        return bbox

"""
Ham_Camera được sử dụng để khởi tạo webcam và chạy mô hình dự đoán của dự án, hình ảnh được ghi nhận từ webcam sẽ được
chuyển thành hình ảnh sau đó cập nhật lên label_cam, tốc dộ cập nhật gần như bằng với thời gian thực
"""
class Ham_Chinh(QMainWindow):
    
    # Lớp Ham_Chinh là lớp chính của chương trình, chịu trách nhiệm khởi tạo các thành phần giao diện và kết nối các tín hiệu giữa các lớp.
    def __init__(self):
        # Gọi hàm khởi tạo của lớp QMainWindow
        super(Ham_Chinh, self).__init__()
        # Tải giao diện từ file ui.ui
        loadUi('main.ui', self)
        
        # Khởi tạo luồng camera
        self.Work = Video()
        self.Work2 = Video2()
        self.thread_camera = Ham_Camera()
        self.thread_camera.luongClearSignal.connect(self.process_string)
        # Khởi tạo luồng video
        self.img_dir = r'D:\a\img'
        self.video_output_path = r'output_video.mp4'
        self.thread_vid = SpeechToVideoThread(self.img_dir, self.video_output_path)
        # Kết nối tín hiệu luongPixMap của luồng camera với hàm setCamera
        self.thread_camera.luongPixMap1.connect(self.setCamera1)
        self.thread_camera.luongPixMap2.connect(self.setCamera2)
        # Kết nối tín hiệu startcam của nút startcam với hàm khoiDongCamera
        self.startcam.clicked.connect(self.khoiDongCamera)
        # Kết nối tín hiệu pausecam của nút pausecam với hàm tamDungCamera
        self.pausecam.clicked.connect(self.tamDungCamera)
        # Kết nối tín hiệu clear của nút clear với hàm xoaToanBo
        self.clear.clicked.connect(self.xoaToanBo)
        # Kết nối tín hiệu delete_2 của nút delete_2 với hàm xoaChu
        self.delete_2.clicked.connect(self.xoaChu)
        self.send.clicked.connect(self.sendMess)
        #Kết nối tín hiệu speak với hàm nói ra văn bản
        # message = client.recv(1024).decode('utf-8')
        # self.text2.setText(message)
        # Kết nối tín hiệu luongString1 của luồng camera với hàm setText của label text
        self.thread_camera.luongString1.connect(self.text1.setText)
        self.thread_camera.luongString2.connect(self.text2.setText)
        #voice to text/video
        self.record_button.clicked.connect(self.start_recording)
        self.stop_record_button.clicked.connect(self.stop_recording)
        self.stop_record_button.setEnabled(False)
        self.play_video.clicked.connect(self.start_video)
        self.stop_video.clicked.connect(self.stop_vide)
        self.thread_vid.audioTextChanged.connect(self.text_2.setText)
    def start_video(self):
        self.Work.start()
        self.Work2.start()
        self.Work.vid.connect(self.Imageupd_slot)
        self.Work2.vid2.connect(self.vidletter)
    def sendMess(self):
        mess = self.text1.text()
        client.send(mess.encode('utf-8'))
    def Imageupd_slot(self, Image):
        self.img_label.setPixmap(QPixmap.fromImage(Image))
    def vidletter(self, Image):
        self.img_label_2.setPixmap(QPixmap.fromImage(Image))
    def stop_vide(self):
        self.Work.stop()
        self.Work2.stop()
    def setCamera1(self, image1):
        # Cập nhật hình ảnh lên label cam
        self.camera1.setPixmap(QPixmap.fromImage(image1))
    def setCamera2(self, image2):
        # Cập nhật hình ảnh lên label cam
        self.camera2.setPixmap(QPixmap.fromImage(image2))
    def khoiDongCamera(self):
        # Khởi động luồng camera để bắt đầu nhận diện vật thể
        self.thread_camera.start()
    def tamDungCamera(self):
        # Dừng luồng camera để tạm dừng nhận diện vật thể
        self.thread_camera.stop()
        # Chờ luồng camera hoàn toàn dừng trước khi tiếp tục
        self.thread_camera.wait()
    def xoaToanBo(self):
        # Xóa toàn bộ nội dung trong label text
        self.thread_camera.luongClearSignal.emit()
    def process_string(self):
        # Truy cập và xử lý giá trị từ Ham_Camera
        self.thread_camera.string = ""  # Thay thế bằng xử lý thực tế của bạn
        # Cập nhật giá trị trong Ham_Camera
        self.thread_camera.luongString1.emit(self.thread_camera.string)
    def xoaChu(self):
        # Xóa ký tự cuối cùng trong textt
        textt = self.text1.text()  
        textt = textt[:-1]
        print(textt)
        # Cập nhật textt lên label text
        self.text1.setText(textt)
    def start_recording(self):
        self.record_button.setEnabled(False)
        self.stop_record_button.setEnabled(True)
        self.thread_vid.start_recording()
    def stop_recording(self):
        self.record_button.setEnabled(True)
        self.stop_record_button.setEnabled(False)
        self.thread_vid.stop_recording()
    import threading

    def listen_for_messages(client, self):
        server_ip = "26.157.245.17"
        client = imagiz.Client("cc1", server_ip=server_ip)
        vid = cv2.VideoCapture(0)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        while True:
            r, frame = vid.read()
            message = client.recv(1024).decode('utf-8')
            self.text2.setText(message)
            if r:
                r, image = cv2.imencode('.jpg', frame, encode_param)
                # cv2.imshow('frame', frame)
                client.send(image)
    listen_thread = threading.Thread(target=listen_for_messages, args=(client,))
    listen_thread.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Ham_Chinh()
    window.setWindowTitle('MainApp')
    window.show()
    sys.exit(app.exec_())