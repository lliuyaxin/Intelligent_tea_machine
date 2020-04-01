#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Author: Liuyaxin <17865196312@163.com>

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
'''
sys.path.append()将不在同一目录下模块的路径添加到程序中
os.path.join()将多个路径组合后返回
os.path.dirname(__file__)返回该脚本所在的完整路径
'''
from xarm.wrapper import XArmAPI
from voice_recognition import Msp
from voice_feedback import Voice_feedback

from pour_tea_01 import Pour_tea_01
from pour_tea_02 import Pour_tea_02

arm_left = XArmAPI('192.168.1.151')
arm_right = XArmAPI('192.168.1.209')    # 连接控制器

arm_left.motion_enable(enable=True)
arm_right.motion_enable(enable=True)    # 使能

arm_left.set_mode(0)
arm_right.set_mode(0)                   # 运动模式：位置控制模式

arm_left.set_state(state=0)
arm_right.set_state(state=0)            # 运动状态：进入运动状态

voice=Msp()
voice_feedback=Voice_feedback()

pt_01=Pour_tea_01(arm_left,arm_right)
pt_02=Pour_tea_02(arm_left,arm_right)

while True:

     text1=voice.run()            # 语音识别
     if "小白" in text1:
         voice_feedback.voice_play("主人.mp3")
         text2= voice.run()
         if "茶" in text2:
             voice_feedback.voice_play("茶种类.mp3")
             text3= voice.run()
             if "大麦" in text3:
                 voice_feedback.voice_play("茶回答.mp3")
                 pt_01.run()
             elif "苦荞" in text3:
                 voice_feedback.voice_play("茶回答.mp3")
                 pt_02.run()
             else:
                 voice_feedback.voice_play("none.mp3")
