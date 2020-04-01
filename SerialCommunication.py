#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Author: Liuyaxin <17865196312@163.com>

import serial
class SerialCommunication(object):
    def ser(self):
        try:
            portx ="COM4"
            bps = 9600
            timex = None
            ser = serial.Serial(portx,bps,timeout=timex)
            print("串口详情参数：", ser)

            result = ser.write(chr(0x08).encode("utf-8"))
            print("写总字节数：", result)

            s=ser.read().hex()
            print(s)
            print("---------------")
            ser.close()
        except Exception as e:
            print("---异常---:",e)
        return s