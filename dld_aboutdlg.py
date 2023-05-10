#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2023-02-17 14:24:38
# @File: dld_aboutdlg.py
# @Author: YeHwong
# @Email: 598316810@qq.com
# @Version ：1.0.0
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QDialog, QPushButton, QVBoxLayout, QHBoxLayout, QLabel
from dld_xml_operate import *


class dld_aboutdlg(QDialog):
    def __init__(self, parent=None):
        super(dld_aboutdlg, self).__init__(parent)
        if cfg_as_updatetool() is False:
            display_text = '<b>Bes Download Tool </b><br>' + '-' * 80 + '<br>' +\
                           'Bes download tool used for its Bluetooth:<br>' + \
                           '- BT: Bluetooth Legacy 3.0<br>' + '- BLE: Bluetooth Low Energy<br>' + \
                           '- BTDM: Bluetooth Dual Mode 4.0<br>' + '-' * 80 + '<br>' + \
                           '<b>Platform: Win32/64</b><br>' + '<b>Version : ' + '3.0' + '</b>'
        else:
            display_text = '<b>Bes Update Tool </b><br>' + '<b>Version : ' + '3.0' + '</b>'
        self.setWindowTitle('About')
        self.setWindowIcon(QIcon('images/about.png'))
        ok = QPushButton('&OK')

        ok.clicked.connect(self.close)
        # self.connect(ok, SIGNAL('clicked()'), self.close)
        pixmap = QPixmap(os.getcwd() + '/images/about.png')
        lbl_img = QLabel()
        lbl_img.setPixmap(pixmap)
        lbl_msg = QLabel(display_text)
        b_layout = QHBoxLayout()
        b_layout.addStretch()
        b_layout.addWidget(ok)
        layouth = QHBoxLayout()
        layouth.addWidget(lbl_img)
        layouth.addWidget(lbl_msg)
        layoutv = QVBoxLayout()
        layoutv.addLayout(layouth)
        layoutv.addLayout(b_layout)
        self.setLayout(layoutv)
