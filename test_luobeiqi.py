#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Author: Liuyaxin <17865196312@163.com>

import os
import sys
import serial

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
cmd_P = [0x4d, 0x4a, 0x08, 0x00, 0xc4, 0x00, 0x00, 0xef]
cmd_N = [0x4d, 0x4a, 0x08, 0x00, 0xe1, 0x00, 0x00, 0xef]
com = serial.Serial('COM5', 115200)

com.write(cmd_P)


