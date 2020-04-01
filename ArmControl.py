#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Author: Liuyaxin <17865196312@163.com>

from threading import Thread
class ArmControl(object):
    def __init__(self,arm_left,arm_right):
        self.arm_left=arm_left
        self.arm_right=arm_right

    def mapper_arm_right(self,shoulder_io,shoulder_fb,elbow_fe,wrist_io,wrist_fe):
        """
        shoulder_io：肩关节内外运动
        shoulder_fb：肩关节前后运动
        elbow_fe：肘关节屈伸运动
        wrist_fe：腕关节掌曲背伸运动
        wrist_io：腕关节内外旋运动
        hand_oc：手掌张合运动
        """
        pr=[]
        if (shoulder_io>135):
            j1=90-shoulder_io
        else:
            j1=90-shoulder_io
        pr.append(j1)
        if shoulder_fb<90:
            j2=-120+(shoulder_fb/90)*30
        else:
            j2=-120+(shoulder_fb-60)
        pr.append(j2)
        if elbow_fe<0:
            j3=-300-elbow_fe
        else:
            j3=-elbow_fe
        pr.append(j3)
        # j4=-180+wrist_io
        j4=0
        pr.append(j4)
        j5=-180+wrist_fe
        pr.append(j5)
        j6=0
        pr.append(j6)
        return pr
    def mapper_arm_left(self,shoulder_io,shoulder_fb,elbow_fe,wrist_io,wrist_fe):
        pl=[]
        if (shoulder_io>135):
            j1=shoulder_io-90
        else:
            j1=shoulder_io-90
        pl.append(j1)
        if shoulder_fb<90:
            j2=-120+(shoulder_fb/90)*30
        else:
            j2=-120+(shoulder_fb-60)
        pl.append(j2)
        if elbow_fe < 0:
            j3 = -300 - elbow_fe
        else:
            j3 = -elbow_fe
        pl.append(j3)
        # j4=-180-wrist_io
        j4=0
        pl.append(j4)
        j5=-180+wrist_fe
        pl.append(j5)
        j6=0
        pl.append(j6)
        return pl

    def initial_right(self):
        self.arm_right.set_servo_angle(angle=[0, -110, -180, -180, 0, 0], speed=30, is_radian=False, wait=True)  # 初始位置
    def initial_left(self):
        self.arm_left.set_servo_angle(angle=[0, -110, -180, -180, 0, 0], speed=30, is_radian=False, wait=True)
    def initial(self):
        i = []
        ir = Thread(target=self.initial_right)
        i.append(ir)
        il = Thread(target=self.initial_left)
        i.append(il)
        for x in i:
            x.start()
        for x in i:
            x.join()

    def move_arm_right(self,shoulder_io_r, shoulder_fb_r, elbow_fe_r, wrist_io_r, wrist_fe_r):
        pr = self.mapper_arm_right(shoulder_io_r, shoulder_fb_r, elbow_fe_r, wrist_io_r, wrist_fe_r)  # 人机映射，得到机械臂关节角度
        self.arm_right.set_servo_angle(angle=pr, speed=100, is_radian=False, wait=True)                # 机械臂运动
    def move_arm_left(self,shoulder_io_l, shoulder_fb_l, elbow_fe_l, wrist_io_l, wrist_fe_l):
        pl = self.mapper_arm_left(shoulder_io_l, shoulder_fb_l, elbow_fe_l, wrist_io_l, wrist_fe_l)
        self.arm_left.set_servo_angle(angle=pl, speed=100, is_radian=False, wait=True)
