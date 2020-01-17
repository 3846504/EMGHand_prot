import sys
from gpiozero import MCP3208
from sklearn.svm import SVC
from sklearn.multiclass import OneVsRestClassifier
from sklearn.externals import joblib
from sklearn.model_selection import train_test_split
import numpy as np
import pandas as pd

import features

def getEmg(dim, ch_num):    #筋電生データ取得　dim:1チャンネル分データの次元数  ch_num:チャンネル数
    ports = [MCP3208(i) for i in range(ch_num)] #ポート開く

    imax = 5000    #データの最大値

    E_data = [[int(imax*ports[i].value) for i in range(ch_num)] for j in range(dim)]    #データ取得

    for i in range(ch_num):
        ports[i].close()    #ポートを閉じる
    sys.exit    #プログラム終了

    return E_data

def model(feature, target):  #モデルの作成   feature:特徴量 target:ラベル
    #========テストデータと分割==========#
    X_train, X_test, y_train, y_test = train_test_split(feature, target, random_state=0)

    #========グリッドサーチの準備========#
    best_score = float(0.0) #最大ベストスコア
    best_param_gamma = 0.01  #ベスト時のガンマ
    best_param_C = 0.0      #ベスト時のC

    progress = 0    #進捗情報

    #========グリッドサーチ開始=========#
    scores = pd.DataFrame()
    for C in np.linspace(0.01, 10, 10):
        svm = SVC(kernel = 'rbf', gamma=0.01, C=C)
        svm.fit(X_train, y_train)
        scores = scores.append(
                {
                    'gamma': 0.01,
                    'C': C,
                    'accuracy': svm.score(X_test, y_test)
                },
                ignore_index=True)
    
        if best_score < svm.score(X_test, y_test):
            best_score = svm.score(X_test, y_test)
            best_param_gamma = 0.01
            best_param_C = C
    
        progress += 10

        print(progress)

    #========ベスト時のパラメータを選択=======#
    gamma = best_param_gamma
    C = best_param_C

    #========ベスト時のパラメータでモデルを作成========#
    svm = SVC(kernel = 'rbf', gamma=gamma, C=C) #モデル作成
    svm.fit(X_train, y_train)
    print("ベストスコア：", round(best_score,2))
    joblib.dump(svm, "/home/pi/project/model/EMG.pkl")  #モデルを出力


def motor(EMG_dim, ch_num):    #モータの制御 pose:予測された手の動作 /0:親指の屈曲、伸展 /1:親指の対立、復位 /2:他4指の屈曲 /3:他4指の伸展
    import RPi.GPIO as GPIO
    import time
    import os

    GPIO.cleanup()
    
    #---- 終了ボタンについてのセットアップ ----#
    BUTTON_PIN = 19
    GPIO.setwarnings(False)
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
        if(GPIO.event_detected(19)):
            GPIO.remove_event_detect(19)
            servo1.stop()
            servo2.stop()
            servo3.stop()
            servo4.stop()
            GPIO.cleanup()
            return 0

        #======必要なデータ取得=======#
        EMG_data = getEmg(EMG_dim*2, ch_num)    #義手を動かすための筋電の生データ取得
        EMG = features.features2(EMG_data)
        
        svm = joblib.load("/home/pi/project/model/EMG.pkl")
        pose = svm.predict([EMG])[0]
        print(pose)

        print(ang1, end=" ")
        print(ang2, end=" ")
        print(ang3, end=" ")
        print(ang4)
        
        if(pose == 0):
            continue
        
        elif(pose == 1):
            if(ang1 >= 15):
                ang1 -= 1
            if(ang3 >= 11):
                ang3 -= 1
            if(ang4 >= 11):
                ang4 -= 1
            servo1.ChangeDutyCycle(ang1)
            servo2.ChangeDutyCycle(ang2)
            servo3.ChangeDutyCycle(ang3)
            servo4.ChangeDutyCycle(ang4)
        
        elif(pose == 2):
            if(ang4 <= 23):
                ang4 += 1
            servo1.ChangeDutyCycle(ang1)
            servo2.ChangeDutyCycle(ang2)
            servo3.ChangeDutyCycle(ang3)
            servo4.ChangeDutyCycle(ang4)
        
        elif(pose == 3):
            if(ang1 <= 23):
                ang1 += 1
            if(ang3 <= 23):
                ang3 += 1
            if(ang4 <= 23):
                ang4 += 1
            servo1.ChangeDutyCycle(ang1)
            servo2.ChangeDutyCycle(ang2)
            servo3.ChangeDutyCycle(ang3)
            servo4.ChangeDutyCycle(ang4)
        
        elif(pose == 4):
            if(ang4 >= 13):
                ang4 -= 1
            servo1.ChangeDutyCycle(ang1)
            servo2.ChangeDutyCycle(ang2)
            servo3.ChangeDutyCycle(ang3)
            servo4.ChangeDutyCycle(ang4)