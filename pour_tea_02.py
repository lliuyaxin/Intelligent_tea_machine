#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Author: Liuyaxin <17865196312@163.com>

import os
import sys
import time
import threading
import serial
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
threadLock = threading.Lock()

cmd_P = [0x4d, 0x4a, 0x08, 0x00, 0xc4, 0x00, 0x00, 0xef]
cmd_N = [0x4d, 0x4a, 0x08, 0x00, 0xe1, 0x00, 0x00, 0xef]

com = serial.Serial('COM5', 115200)


class Pour_tea_02(object):
    def __init__(self,arm_left,arm_right):

        global flag
        flag = [0]
        self.arm_left=arm_left
        self.arm_right=arm_right

    def initial_poition(self):
        self.arm_left.set_position(x=131, y=-97, z=133, roll=0, pitch=90, yaw=-90, speed=1000, is_radian=False, wait=True)
        self.arm_right.set_position(x=167, y=97, z=141, roll=-90, pitch=85, yaw=0, speed=1000, is_radian=False, wait=True)

    def pour_tea_left(self):
        #准备
        self.arm_left.set_position(x=131, y=-15, z=115, roll=110, pitch=85, yaw=20, speed=1000, is_radian=False, wait=True)
        #等待杯子落下
        self.arm_left.set_position(x=132, y=-165.5, z=150.2, roll=90.1, pitch=83.3, yaw=-19.9, speed=50, is_radian=False, wait=True)
        # 打开机械爪
        # self.arm_left.set_tgpio_digital(1, 0)
        # self.arm_left.set_tgpio_digital(0, 1)
        #落杯
        threadLock.acquire()
        com.write(cmd_P)
        threadLock.release()
        time.sleep(3)
        # 拿杯子
        self.arm_left.set_position(x=112, y=-159.4, z=86.4, roll=90.1, pitch=83.3, yaw=-19.9, speed=50, is_radian=False, wait=True)
        self.arm_left.set_position(x=112, y=-159.4, z=170, roll=90.1, pitch=83.3, yaw=-19.9, speed=1000, is_radian=False, wait=True)
        self.arm_left.set_position(x=345, y=-165, z=170, roll=-70, pitch=90, yaw=180, speed=1000, is_radian=False, wait=True)
        #到达放茶叶位置
        self.arm_left.set_position(x=460, y=-400, z=170, roll=0, pitch=90, yaw=-90, speed=100, is_radian=False, wait=True)
        while flag[0]==1:
            time.sleep(0.1)
        #放茶叶
        # time.sleep(3)
        #到达饮水机位置
        self.arm_left.set_position(x=384, y=-408, z=130, roll=-123, pitch=90, yaw=86, speed=1000, is_radian=False, wait=True)
        self.arm_left.set_position(x=296, y=-408, z=130, roll=-123, pitch=90, yaw=86, speed=1000, is_radian=False, wait=True)
        while flag[0]==2:
            time.sleep(0.1)
        #接水
        time.sleep(6)
        #端茶
        self.arm_left.set_position(x=414.8, y=-307.8, z=100.5, roll=2.3, pitch=84.4, yaw=-57.9, speed=1000, is_radian=False,  wait=True)
        # self.arm_left.set_position(x=414.8, y=-307.8, z=60.5, roll=2.3, pitch=84.4, yaw=-57.9, speed=1000, is_radian=False,  wait=True)
        #
        # self.arm_left.set_position(x=328.7, y=-241, z=74.6, roll=-115.3, pitch=84.1, yaw=-167.3, speed=1000, is_radian=False,  wait=True)
        # #等主人取茶
        time.sleep(5)
        #复位
        # self.arm_left.set_position(x=405.8, y=-191.8, z=62.6, roll=-14.5, pitch=87.6, yaw=144, speed=1000, is_radian=False, wait=True)
        self.arm_left.set_position(x=131, y=-15, z=115, roll=110, pitch=85, yaw=20, speed=1000, is_radian=False, wait=True)


    def pour_tea_right(self):
        #准备
        self.arm_right.set_position(x=225, y=15, z=115, roll=-110, pitch=85, yaw=-20, speed=1000, is_radian=False, wait=True)
        #等待杯子落下
        self.arm_right.set_position(x=225, y=80, z=115, roll=-110, pitch=85, yaw=-20, speed=1000, is_radian=False, wait=True)
        time.sleep(2)
        flag[0]=1
        #移动到茶叶位置
        self.arm_right.set_position(x=545.8, y=-5.7, z=106.8, roll=-103.4, pitch=85.3, yaw=-13.5, speed=1000, is_radian=False, wait=True)
        self.arm_right.set_tgpio_digital(1, 0)
        self.arm_right.set_tgpio_digital(0, 1)        # 打开机械爪

        self.arm_right.set_position(x=545.8, y=167, z=106.8, roll=112.6, pitch=87.2, yaw=-157.6, speed=100, is_radian=False, wait=True)
        #拿起茶盒
        self.arm_right.set_tgpio_digital(0, 0)
        self.arm_right.set_tgpio_digital(1, 1)      # 关闭机械爪
        #移动到倒茶位置
        time.sleep(1)
        self.arm_right.set_position(x=392, y=230, z=300, roll=70, pitch=88, yaw=123, speed=1000, is_radian=False, wait=True)
        #倒茶叶
        self.arm_right.set_servo_angle(angle=[37.4,0.4,-51.2,212.2,24,-160.2], speed=180, is_radian=False, wait=True)
        self.arm_right.set_position(x=392, y=230, z=300, roll=70, pitch=88, yaw=123, speed=1000, is_radian=False, wait=True)
        flag[0] = 2
        #放下茶盒
        self.arm_right.set_position(x=545.8, y=167, z=106.8, roll=112.6, pitch=87.2, yaw=-157.6, speed=100, is_radian=False, wait=True)
        self.arm_right.set_tgpio_digital(1, 0)
        self.arm_right.set_tgpio_digital(0, 1)        # 打开机械爪
        self.arm_right.set_position(x=545.8, y=-5.7, z=106.8, roll=-103.4, pitch=85.3, yaw=-13.5, speed=1000, is_radian=False, wait=True)
        # self.arm_right.set_tgpio_digital(0, 0)
        # self.arm_right.set_tgpio_digital(1, 1)        # 关闭机械爪
        self.arm_right.set_position(x=545.8, y=-5.7, z=282, roll=-103.4, pitch=85.3, yaw=-13.5, speed=1000, is_radian=False, wait=True)
        self.arm_right.set_position(x=330, y=327, z=282, roll=-90, pitch=85, yaw=32, speed=1000, is_radian=False, wait=True)
        # 按按钮
        self.arm_right.set_position(x=305, y=327, z=282, roll=-90, pitch=85, yaw=32, speed=1000, is_radian=False, wait=True)
        flag[0]=0
        #接水
        time.sleep(6)
        #等待端杯子
        # self.arm_right.set_position(x=300, y=170, z=170, roll=-90, pitch=85, yaw=-20, speed=50, is_radian=False, wait=True)
        # self.arm_right.set_position(x=290, y=333, z=170, roll=-90, pitch=85, yaw=-20, speed=50, is_radian=False, wait=True)
        # 一起端水
        # self.arm_right.set_position(x=440, y=295, z=328, roll=-90, pitch=85, yaw=-20, speed=50, is_radian=False, wait=True)
        # 复位
        self.arm_right.set_position(x=300, y=80, z=190, roll=-90, pitch=85, yaw=0, speed=1000, is_radian=False, wait=True)
        self.arm_right.set_position(x=225, y=15, z=115, roll=-110, pitch=85, yaw=-20, speed=100, is_radian=False, wait=True)


    def run(self):

        l=threading.Thread(target=self.pour_tea_left)
        r=threading.Thread(target=self.pour_tea_right)
        l.start()
        r.start()
        l.join()
        r.join()
