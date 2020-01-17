#!/usr/bin/python 
# coding:utf-8 
import time
import RPi.GPIO as GPIO
import os

def selectMode(num):
    pin1 = 21
    pin2 = 26
    pin3 = 5
    pin4 = 13
    pin5 = 16

    try:
        pinnumber=19
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(pin1, GPIO.OUT) # GPIOを出力として使用する
        GPIO.setup(pin2, GPIO.OUT)
        GPIO.setup(pin3, GPIO.OUT)
        GPIO.setup(pin4, GPIO.OUT)
        GPIO.setup(pin5, GPIO.OUT)

        GPIO.output(pin2, GPIO.HIGH)
        GPIO.output(pin3, GPIO.LOW)
        GPIO.output(pin4, GPIO.LOW)
        GPIO.output(pin5, GPIO.LOW)
        GPIO.output(pin1, GPIO.LOW)

        #GPIO23pinを入力モードとし、pull up設定とします 
        GPIO.setup(pinnumber,GPIO.IN,pull_up_down=GPIO.PUD_UP)

        flag = 0

        while True:
            GPIO.wait_for_edge(pinnumber, GPIO.FALLING)
            sw_counter = 0

            while True:
                sw_status = GPIO.input(pinnumber)
                if sw_status == 0:
                    sw_counter = sw_counter + 1
                    if sw_counter >= 50:
                        print("長押し検知！")
                        #GPIO.cleanup()
                        return flag%num
                else:
                    print("短押し検知")
                    flag += 1
                    print(flag%num)
                    break

                time.sleep(0.01)
            
            if(flag%num == 0):
                GPIO.output(pin2, GPIO.HIGH) 
                GPIO.output(pin3, GPIO.LOW)
                GPIO.output(pin4, GPIO.LOW)
                GPIO.output(pin5, GPIO.LOW)
                GPIO.output(pin1, GPIO.LOW)
            if(flag%num == 1):
                GPIO.output(pin3, GPIO.HIGH)
                GPIO.output(pin2, GPIO.LOW)
                GPIO.output(pin4, GPIO.LOW)
                GPIO.output(pin5, GPIO.LOW)
                GPIO.output(pin1, GPIO.LOW)
            if(flag%num == 2): 
                GPIO.output(pin4, GPIO.HIGH)
                GPIO.output(pin2, GPIO.LOW)
                GPIO.output(pin3, GPIO.LOW)
                GPIO.output(pin5, GPIO.LOW)
                GPIO.output(pin1, GPIO.LOW)
            if(flag%num == 3):
                GPIO.output(pin5, GPIO.HIGH)
                GPIO.output(pin2, GPIO.LOW)
                GPIO.output(pin3, GPIO.LOW)
                GPIO.output(pin4, GPIO.LOW)
                GPIO.output(pin1, GPIO.LOW)
            if(flag%num == 4):
                GPIO.output(pin1, GPIO.HIGH)
                GPIO.output(pin2, GPIO.LOW)
                GPIO.output(pin3, GPIO.LOW)
                GPIO.output(pin4, GPIO.LOW)
                GPIO.output(pin5, GPIO.LOW)

    except(KeyboardInterrupt):
        GPIO.cleanup()

if __name__ == "__main__":
    selectMode(5)