#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Author: Liuyaxin <17865196312@163.com>

import os
import sys
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))

from xarm.wrapper import XArmAPI

arm = XArmAPI('192.168.1.209')
# arm = XArmAPI('192.168.1.151')

arm.motion_enable(enable=True)
arm.set_mode(0)
arm.set_state(state=0)

# arm.reset(wait=True)

arm.set_position(x=214.1, y=18.9, z=101.6, roll=-117.6, pitch=88.8, yaw=-27.5, speed=50, is_radian=False, wait=True)
# arm.set_position(x=223.9, y=18.9, z=101.6, roll=-117.6, pitch=88.8, yaw=-27.5, speed=50, is_radian=False, wait=True)

# 打开机械爪
# arm.set_gpio_digital(2, 0)
# arm.set_gpio_digital(1, 1)
arm.set_tgpio_digital(1, 1)
arm.set_tgpio_digital(0, 1)
# time.sleep(1)
arm.set_position(x=315, y=95, z=250, roll=-90, pitch=180, yaw=0, speed=50, is_radian=False, wait=True)
# 关闭机械爪
# arm.set_gpio_digital(1, 0)
# arm.set_gpio_digital(2, 1)
arm.set_tgpio_digital(0, 0)
arm.set_tgpio_digital(1, 1)

arm.disconnect()