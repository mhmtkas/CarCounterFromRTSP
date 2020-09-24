from threading import Thread
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QStyle, QSizePolicy, \
    QLineEdit, QLabel, QVBoxLayout, QSlider
import sys
import collections
from datetime import datetime
from PyQt5.QtGui import QIcon, QPalette, QImage, QPixmap
from PyQt5.QtCore import Qt, QUrl
import cv2
from smtplib import SMTP
from email.mime.image import MIMEImage



global sayac
sayac = 0


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.processthread = Thread(target=self.process_video)
        self.savethreadd = Thread(target=self.save264)
        self.sendthread = Thread(target=self.sendMail)
        Params = collections.namedtuple('Params', ['a', 'b', 'c'])
        self.playBtn = QPushButton()
        self.processBtn = QPushButton()
        self.stopBtn = QPushButton()
        self.setWindowTitle("Piton Ar-Ge")
        self.setGeometry(350, 100, 700, 500)
        self.setWindowIcon(QIcon('player.png'))

        p = self.palette()
        p.setColor(QPalette.Window, Qt.white)
        self.setPalette(p)

        self.init_ui()

        self.show()

    def init_ui(self):

        self.exit = 0
        self.processBtn.setEnabled(False)

        # create button for playing

        self.playBtn.setEnabled(True)
        self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playBtn.setText('Play')
        self.processBtn.setIcon(self.style().standardIcon(QStyle.SP_ArrowForward))
        self.processBtn.setText('Analyze')
        self.stopBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))

        self.playBtn.clicked.connect(self.play_video)
        self.processBtn.clicked.connect(self.threadprocess)

        # getting rtsp link

        self.link = QLineEdit()
        self.mail = QLineEdit()
        self.nmbrofcars = QLineEdit()
        self.linklabel = QLabel('''<font size="4" color="red">Link:            </font>''')
        self.maillabel = QLabel('''<font size="4" color="red">Mail:            </font>''')
        self.nmbrofcarslabel = QLabel('''<font size="4" color="red">Number of Vehicles: </font>''')
        self.yatay = QSlider()
        self.yatay.setValue(50)
        self.dikey = QSlider()
        self.dikey.setValue(50)
        self.yatay2 = QSlider()
        self.yatay2.setValue(200)
        self.dikey2 = QSlider()
        self.dikey2.setValue(200)
        self.yatay.setRange(0, 500)
        self.dikey.setRange(0, 500)
        self.yatay2.setRange(0, 500)
        self.dikey2.setRange(0, 500)
        self.yatay.setOrientation(Qt.Horizontal)
        self.dikey.setOrientation(Qt.Vertical)
        self.yatay2.setOrientation(Qt.Horizontal)
        self.dikey2.setOrientation(Qt.Vertical)

        # create label

        self.label = QLabel('''<font size="2" color="black">Piton Ar-Ge Intern EEE - Mehmet Kaş </font>''')
        self.label2 = QLabel('''<font size="4" color="black">First Point </font>''')
        self.label3 = QLabel('''<font size="4" color="black">Second Point </font>''')
        self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # create hbox and vbox layouts

        sliderLayout = QVBoxLayout()
        hboxLayout = QHBoxLayout()
        hboxLayout1 = QHBoxLayout()
        hboxLayout2 = QHBoxLayout()
        hboxLayout3 = QHBoxLayout()
        hboxLayout4 = QHBoxLayout()
        hboxLayout1.setContentsMargins(0, 0, 0, 0)
        hboxLayout1.addWidget(self.playBtn)

        # hboxLayout1.addWidget(self.stopBtn)

        hboxLayout1.addWidget(self.processBtn)
        sliderLayout.addWidget(self.label2)
        sliderLayout.addWidget(self.dikey)
        sliderLayout.addWidget(self.yatay)
        sliderLayout.addWidget(self.label3)
        sliderLayout.addWidget(self.dikey2)
        sliderLayout.addWidget(self.yatay2)
        hboxLayout2.addWidget(self.linklabel)
        hboxLayout2.addWidget(self.link)
        hboxLayout3.addWidget(self.maillabel)
        hboxLayout3.addWidget(self.mail)
        hboxLayout4.addWidget(self.nmbrofcarslabel)
        hboxLayout4.addWidget(self.nmbrofcars)

        # create vbox layout

        vboxLayout = QVBoxLayout()
        vboxLayout.addLayout(hboxLayout2)
        vboxLayout.addLayout(hboxLayout3)
        vboxLayout.addLayout(hboxLayout4)
        vboxLayout.addLayout(hboxLayout1)
        hboxLayout.addLayout(vboxLayout)
        hboxLayout.addLayout(sliderLayout)
        vboxLayout.addWidget(self.label)
        self.setLayout(hboxLayout)
        self.setWindowIcon(QIcon('pythonlogo.png'))

    def play_video(self):

        cap = cv2.VideoCapture(self.link.text())
        self.processBtn.setEnabled(True)
        self.playBtn.setEnabled(False)
        while True:
            _, frame = cap.read()

            cv2.line(frame, (self.yatay2.value(), self.dikey2.value()), (self.yatay.value(), self.dikey.value()),
                     (0, 255, 0), 2)

            cv2.imshow("Frame", frame)

            key = cv2.waitKey(25)
            if key == 27 or self.exit == 1:
                break

        cap.release()
        cv2.destroyAllWindows()

    def process_video(self):
        global j
        j = 1

        cap = cv2.VideoCapture(self.link.text())

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        kernel3 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))

        substractor = cv2.createBackgroundSubtractorMOG2(varThreshold=150, detectShadows=False)

        self.sayac = 0
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))

        # save as .264
        fourcc = cv2.VideoWriter_fourcc('H', '2', '6', '4')
        kayit = cv2.VideoWriter('kayit.264', fourcc, 10, (frame_width, frame_height))

        while True:
            _, frame = cap.read()
            self.exit = 1
            mask = substractor.apply(frame)

            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

            mask = cv2.erode(mask, kernel2, iterations=1)
            mask = cv2.dilate(mask, kernel3, iterations=1)


            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            # cv2.drawContours(frame, contours, -1, (0,255,0), 3)

            cv2.line(frame, (self.yatay.value(), self.dikey.value()), (self.yatay2.value(), self.dikey2.value()),
                     (0, 255, 0), 2)
            m=self.egimofline()

            if 1 >= m >= 0:
                self.detectlinedikey = int((self.dikey2.value()+self.dikey.value())/2)
                for contour, in zip(contours):
                    (x, y, w, h) = cv2.boundingRect(contour)
                    a = int(w / 2)
                    b = int(h / 2)
                    if w > 20 and h > 20 :
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                        centroid = (x + a, y + b)
                        cv2.drawMarker(frame, centroid, (0, 255, 0), markerType=50, markerSize=10)

                        if self.yatay.value() < x + a<self.yatay2.value() and self.detectlinedikey-2 < y + b < \
                                self.detectlinedikey + 2:
                            self.sayac += 1
                            self.saveJson()
                            print(self.sayac)
            elif m > 1:
                self.detectlineyatay = int((self.yatay2.value() + self.yatay.value()) / 2)
                for contour, in zip(contours):
                    (x, y, w, h) = cv2.boundingRect(contour)
                    a = int(w / 2)
                    b = int(h / 2)
                    if w > 20 and h > 20 :
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                        centroid = (x + a, y + b)
                        cv2.drawMarker(frame, centroid, (0, 255, 0), markerType=50, markerSize=10)

                        if self.detectlineyatay-2 < x + a < self.detectlineyatay + 2 and self.dikey2.value() < y + b < \
                                self.dikey.value():
                            self.sayac += 1
                            self.saveJson()
                            print(self.sayac)
            else:
                break


            """for contour, in zip(contours):
                (x, y, w, h) = cv2.boundingRect(contour)
                a = int(w / 2)
                b = int(h / 2)
                if w > 20 and h > 20 and y + b > 70:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    centroid = (x + a, y + b)
                    cv2.drawMarker(frame, centroid, (0, 255, 0), markerType=50, markerSize=10)

                    if self.yatay.value() < x + a and self.dikey.value() < y + b:
                        self.sayac += 1
                        self.saveJson()
                        print(self.sayac)"""
            cv2.putText(frame, "Vehicle: " + str(self.sayac), (50, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 250, 0), 2)

            self.t = int(self.nmbrofcars.text())

            if (self.sayac == self.t) & (j == 1):
                cv2.imwrite('resim3.jpg', frame)
                self.sendMail()
                j = 0

            kayit.write(frame)

            # write as .bin
            # with open('file1.bin', 'ab') as f:
            #   f.write(frame)
            # self.save264()
            cv2.imshow("Frame", frame)
            cv2.imshow("mask", mask)

            key = cv2.waitKey(25)
            if key == 27:
                break

        cap.release()
        kayit.release()
        cv2.destroyAllWindows()

    def sendMail(self):

        subject = "Piton Ar-Ge Internship"
        message = "Bu bir test mesajıdır."

        fp = open('resim3.jpg', 'rb')
        msgImage = MIMEImage(fp.read())
        fp.close()

        self.myMailAddress = "sending_mail@gmail.com"  # sending mail should be entered here
        password = "sending_mail_password"  # sending mail's password should be entered here

        self.sendTo = self.mail.text()

        mail = SMTP("smtp.gmail.com", 587)
        mail.ehlo()
        mail.starttls()
        mail.login(self.myMailAddress, password)
        print("wait")
        mail.sendmail(self.myMailAddress, self.sendTo, msgImage.as_string())

        print("mail gönderme işlemi başarılı")

    def save264(self):

        frame_width = int(self.cap.get(3))
        frame_height = int(self.cap.get(4))

        # save as .264
        fourcc = cv2.VideoWriter_fourcc('H', '2', '6', '4')
        kayit = cv2.VideoWriter('kayit.264', fourcc, 10, (frame_width, frame_height))

        kayit.write(self.frame)

    def threadprocess(self):
        self.processthread.start()

    def savethread(self):
        self.savethreadd.start()

    def sendmailthread(self):
        self.sendthread.start()

    def saveJson(self):

        time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        dosya = open("data.json", "a")
        if self.sayac == 1:
            dosya.write("\n")

        dosya.write(str(self.sayac) + ". car detected at " + time + "\n")


        dosya.close()





    def egimofline(self):

        m = (self.dikey2.value()-self.dikey.value())/(self.yatay2.value()-self.yatay.value())

        return abs(m)


app = QApplication(sys.argv)
win = Window()
win.show()
sys.exit(app.exec_())
