#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2023-02-17 14:27:40
# @File: dld_setportdlg.py
# @Author: YeHwong
# @Email: 598316810@qq.com
# @Version ：1.0.0
"""
    设置串口列表对话框。
"""

import serial.tools.list_ports
import dld_global as dld_g
from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QLineEdit, QCheckBox
from dld_xml_operate import *
from dld_string_res import *


lang_set = get_xmlcfg_language()
if lang_set == 'en':
    qtCreatorFile = 'setportdlg_en.ui'
else:
    qtCreatorFile = 'setportdlg.ui'
Ui_SetportDlg, QtBaseClass = uic.loadUiType(qtCreatorFile)


class dld_setportdlg(QDialog, Ui_SetportDlg):

    def __init__(self):
        QDialog.__init__(self)
        Ui_SetportDlg.__init__(self)
        self.setupUi(self)
        self.tableWidget.setHorizontalHeaderLabels([str_port_num[lang_set], str_com[lang_set]])
        self.Port_list = []
        self.PortNum = []
        self.LineCom = []
        self.LineBaud = []
        self.length = 0
        self.bt_addr_dis = None
        self.ble_addr_dis = None
        for i in range(0, 10):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(''))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(''))
        self.autocheckButton.clicked.connect(self.auto_check)
        self.OkButton.clicked.connect(self.Ok)
        self.Canclebutton.clicked.connect(self.cancel)
        # self.connect(self.autocheckButton, SIGNAL('clicked()'), self.autocheck)
        # self.connect(self.OkButton, SIGNAL('clicked()'), self.Ok)
        # self.connect(self.Canclebutton, SIGNAL('clicked()'), self.Cancle)
        return

    def Ok(self):
        if len(self.Port_list) == 0:
            self.accept()
            return
        checked_port_num = 0
        for loop_index in range(self.length):
            if self.Port_list[loop_index].isChecked():
                checked_port_num += 1

        loop_index = 0
        while True:
            port_set = self.Port_list[loop_index]
            port_num = self.PortNum[loop_index]
            if not port_set.isChecked():
                self.Port_list.remove(port_set)
                self.PortNum.remove(port_num)
                if len(self.Port_list) == checked_port_num:
                    break
                loop_index = 0
            else:
                loop_index += 1
                if loop_index >= self.length:
                    break

        row_count = len(self.Port_list)
        if row_count == 0:
            self.accept()
            return
        dld_g.settotalportnum(row_count)
        for i in range(row_count):
            dld_g.setportNum(i, self.PortNum[i])
            dld_g.setportUsed(i, self.Port_list[i].isChecked())

        self.accept()

    def cancel(self):
        self.reject()

    def auto_check(self):
        serial_list = []
        port_list = list(serial.tools.list_ports.comports())
        com_count = len(port_list)
        for i in range(0, com_count):
            port_n = port_list[i]
            try:
                s = serial.Serial(port_n[0])
                serial_list.append(int(port_n[0].split('COM')[1]))
                s.close()
            except serial.SerialException:
                pass

        serial_list.sort()
        self.length = len(serial_list)
        self.Port_list = []
        self.LineCom = []
        self.LineBaud = []
        self.tableWidget.clear()
        self.tableWidget.setHorizontalHeaderLabels([str_port_num[lang_set], str_com[lang_set]])
        for i in range(0, 10):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(''))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(''))

        for i in range(self.length):
            index = serial_list[i]
            self.PortNum.append(index)
            self.Port_list.append(QCheckBox('COM'))
            self.Port_list[i].setChecked(True)
            self.tableWidget.setCellWidget(i, 0, self.Port_list[i])
            self.LineCom.append(QLineEdit('%d' % index))
            self.LineCom[i].setEnabled(False)
            self.LineCom[i].setContextMenuPolicy(Qt.NoContextMenu)
            self.LineCom[i].setFocusPolicy(Qt.StrongFocus)
            self.tableWidget.setCellWidget(i, 1, self.LineCom[i])
