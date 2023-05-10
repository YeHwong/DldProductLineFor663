#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2023-02-17 14:29:26
# @File: error_report.py
# @Author: YeHwong
# @Email: 598316810@qq.com
# @Version ：1.0.0
import os

import dld_xml_operate
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QDialog, QPushButton, QLabel, QHBoxLayout, QVBoxLayout
from dld_string_res import *


class ErrorReportDlg(QDialog):

    def __init__(self, error_text):
        super(ErrorReportDlg, self).__init__()
        self.long_set = dld_xml_operate.get_xmlcfg_language()
        self.setWindowTitle(str_error[self.long_set])
        self.setWindowIcon(QIcon('images/error.png'))
        ok_btn = QPushButton(str_ok[self.long_set])
        ok_btn.clicked.connect(self.close)
        # self.connect(ok_btn, SIGNAL('clicked()'), self.close)
        qpixmap_obj = QPixmap(os.getcwd() + '/images/error.png')
        lbl_img = QLabel()
        lbl_img.setPixmap(qpixmap_obj)
        lbl_msg = QLabel(error_text)
        b_layout = QHBoxLayout()
        b_layout.addStretch()
        b_layout.addWidget(ok_btn)
        layout_h = QHBoxLayout()
        layout_h.addWidget(lbl_img)
        layout_h.addWidget(lbl_msg)
        layoutv = QVBoxLayout()
        layoutv.addLayout(layout_h)
        layoutv.addLayout(b_layout)
        self.setLayout(layoutv)