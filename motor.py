from sklearn.externals import joblib
from rasp_tool import getEmg, features
from multiprocessing import Process, Value
import time

def check(pose, EMG_dim, ch_num):
    while(True):
        EMG_data = getEmg(EMG_dim*2, ch_num)    #義手を動かすための筋電の生データ取得
        EMG = features.features2(EMG_data)

        svm = joblib.load("/home/pi/project/model/EMG.pkl")
        pose.value = svm.predict([EMG])[0]

def motor(EMG_dim, ch_num):
    pose = Value("d", 0)
    Process(target=check, args=(pose, EMG_dim, ch_num)).start()

    import RPi.GPIO as GPIO
    import time
    import os

    
    #---- 終了ボタンについてのセットアップ ----#
    BUTTON_PIN = 19
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN,GPIO.IN) 
    GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, bouncetime=300)
    #------------------------------------#
    
    #---- モータについてのセットアップ ----#
    gp_out1 = 18
    gp_out2 = 17
    gp_out3 = 27
    gp_out4 = 24

    GPIO.setup(gp_out1, GPIO.OUT)
    GPIO.setup(gp_out2, GPIO.OUT)
    GPIO.setup(gp_out3, GPIO.OUT)
    GPIO.setup(gp_out4, GPIO.OUT)

    #700µs~2300µs(270°) neutral=1500µs
    #電源投入より0.5秒信号をLに
    #7~23%
    servo1 = GPIO.PWM(gp_out1, 100)
    servo2 = GPIO.PWM(gp_out2, 100)
    servo3 = GPIO.PWM(gp_out3, 100)
    servo4 = GPIO.PWM(gp_out4, 100)
    #-------------------------------------#
    
    #---- 動作開始 ----#
    #パルスの初期化 5秒間の間に電源を入れる
    servo1.start(0)
    servo2.start(0)
    servo3.start(0)
    servo4.start(0)

    time.sleep(5)

    ang1 = 20
    ang2 = 20
    ang3 = 20
    ang4 = 20

    servo1.ChangeDutyCycle(ang1)
    servo2.ChangeDutyCycle(ang2)
    servo3.ChangeDutyCycle(ang3)
    servo4.ChangeDutyCycle(ang4)

    while(True):
        print(int(pose.value))
        time.sleep(0.1)

        print(ang1, end=" ")
        print(ang2, end=" ")
        print(ang3, end=" ")
        print(ang4)

        if(GPIO.event_detected(19)):
            GPIO.remove_event_detect(19)
            servo1.stop()
            servo2.stop()
            servo3.stop()
            servo4.stop()
            GPIO.cleanup()
            return 0

        if(int(pose.value) == 0):
            continue
        
        elif(int(pose.value) == 1):
            if(ang1 >= 15):
                ang1 -= 0.5
            if(ang3 >= 11):
                ang3 -= 0.5
            if(ang4 >= 15):
                ang4 -= 0.5
            servo1.ChangeDutyCycle(ang1)
            servo3.ChangeDutyCycle(ang3)
            servo4.ChangeDutyCycle(ang4)
        
        elif(int(pose.value) == 2):
            if(ang4 <= 23):
                ang4 += 0.5
            servo4.ChangeDutyCycle(ang4)
        
        elif(int(pose.value) == 3):
            if(ang1 <= 23):
                ang1 += 0.5
            if(ang3 <= 23):
                ang3 += 0.5
            if(ang4 <= 23):
                ang4 += 0.5
            servo1.ChangeDutyCycle(ang1)
            servo3.ChangeDutyCycle(ang3)
            servo4.ChangeDutyCycle(ang4)
        
        elif(int(pose.value) == 4):
            if(ang4 >= 13):
                ang4 -= 0.5
            servo4.ChangeDutyCycle(ang4)
        
        else:
            print("hoge")


if __name__ == "__main__":
    motor(100, 5)