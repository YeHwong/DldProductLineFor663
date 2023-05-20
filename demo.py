#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2023-05-14 9:25
# @File: demo.py
# @Author: YeHwong
# @Email: 598316810@qq.com
# @Version ：1.0.0#!/usr/bin/python3
# # 提供了与 C 兼容的数据类型，并允许调用 DLL 或共享库中的函数

import ctypes
import serial
import time

class PortCtrl:
    def __init__(self):
        self.ser = serial.Serial()
        self.port_num = "COM13"
        self.timer = Timer()

    def open_port(self):
        self.ser.port = self.port_num
        self.ser.baudrate = 115200  # 串口设置：波特率
        self.ser.timeout = 5  # 串口设置：超时时间
        self.ser.write_timeout = 0.5  # 串口设置：写入超时
        self.ser.interCharTimeout = 0.01  # 串口设置：字符间超时
        self.ser.inter_byte_timeout = 0.01  # 串口设置：字节间超时
        try:
            self.ser.open()
        except Exception as e:
            print(e)
            return None

    def close_port(self):
        try:
            self.ser.close()
        except Exception as e:
            print(e)

    def rts_ctrl(self):
        self.ser.setRTS(1)
        self.timer.msleep(1500)
        self.ser.setRTS(0)
        self.timer.msleep(400)
        for i in range(1, 5):
            self.ser.setRTS(1)
            self.timer.msleep(4.8)
            self.ser.setRTS(0)
            self.timer.msleep(4.8)
        self.timer.msleep(4.8)
        self.ser.setRTS(1)
        self.timer.msleep(4.8)
        for i in range(1, 5):
            self.ser.setRTS(1)
            self.timer.msleep(4.8)
            self.ser.setRTS(0)
            self.timer.msleep(4.8)
        print("波形输出完成！！！")


class Timer(object):

    def __init__(self):
        freq = ctypes.c_longlong(0)
        ctypes.windll.kernel32.QueryPerformanceFrequency(ctypes.byref(freq))
        self.__freq = freq.value
        self.__beginCount = self.counter()

    def counter(self):
        freq = ctypes.c_longlong(0)
        ctypes.windll.kernel32.QueryPerformanceCounter(ctypes.byref(freq))
        return freq.value

    def beginCount(self):
        self.__beginCount = self.counter()

    # 时间差，精确到微秒
    def secondsDiff(self):
        self.__endCount = self.counter()
        return (self.__endCount - self.__beginCount) / (self.__freq + 0.)

    # 休眠，精确到毫秒
    def msleep(self, timeout):
        self.__beginCount = self.counter()
        while True:
            self.__endCount = self.counter()
            if ((self.__endCount - self.__beginCount) / (self.__freq + 0.)) * 1000 >= timeout:
                print('dt={}'.format(((self.__endCount - self.__beginCount) / (self.__freq + 0.)) * 1000))
                return

if __name__ == '__main__':
    pc = PortCtrl()
    pc.open_port()
    pc.rts_ctrl()
    pc.close_port()
