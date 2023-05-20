#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2023年2月17日 14点20分
# @File: dld_mainwnd.py
# @Author: YeHwong
# @Email: 598316810@qq.com
# @Version ：1.0.0
import shutil
import threading
import time
from hashlib import md5
from win32api import GetSystemMetrics
from multiprocessing import Pipe
from PyQt5.QtWidgets import QMainWindow, QProgressBar, QTableWidget, QWidget, QDockWidget, QTextBrowser, QFrame, \
    QLCDNumber, QLineEdit, QAction, QTableWidgetItem, QCheckBox, QMessageBox, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor, QFont, QIcon

import dld_global as dld_g

from dld_aboutdlg import dld_aboutdlg
from dld_setportdlg import dld_setportdlg
from dld_subprocess import DldProcess
from dld_monitorstep import Timer, DldProgressMonitor
from dld_xml_operate import *
from dld_login import dld_login
from dld_string_res import *
from error_report import ErrorReportDlg
from cfg_json_parse import *

# importlib.reload(sys)
# sys.setdefaultencoding('utf8')
DEFAULT_STYLE = '\nQProgressBar{\n    border: 2px solid grey;\n    border-radius: 5px;\n    text-align: ' \
                'center\n}\nQProgressBar::chunk {\n    background-color: lightblue;\n    width: 10px;\n    margin: ' \
                '1px;\n}\n '
COMPLETED_STYLE1 = '\nQProgressBar{\n    border: 2px solid grey;\n    border-radius: 5px;\n    text-align: ' \
                   'center\n}\nQProgressBar::chunk {\n    background-color: #FFFF00;\n    width: 10px;\n    margin: ' \
                   '1px;\n}\n '
COMPLETED_STYLE = '\nQProgressBar{\n    border: 2px solid grey;\n    border-radius: 5px;\n    text-align: ' \
                  'center\n}\nQProgressBar::chunk {\n    background-color: #00FF00;\n    width: 10px;\n    margin: ' \
                  '1px;\n}\n '


def gui_getopt(job):
    index = job['index']
    return dld_g.opt_array[index]


def gui_getprogressbar(job):
    index = job['index']
    return bar_array[index]


def gui_getcalibvalue(job):
    index = job['index']
    return calib_value_array[index]


def getSTATE(job):
    index = job['index']
    return STATE_array[index]


def gui_get_btaddr_display(job):
    index = job['index']
    if index != -1:
        return dld_g.g_btaddr_display_array[index]
    else:
        return


def gui_get_bleaddr_display(job):
    index = job['index']
    if index != -1:
        return dld_g.g_bleaddr_display_array[index]
    else:
        return


def gui_getTIME(job):
    index = job['index']
    return TIME_array[index]


def gui_getmonitorthrd(job):
    index = job['monitorthrdindex']
    return dld_g.g_monitorthrd_array[index]


class XProgressBar(QProgressBar):

    def __init__(self, parent=None):
        QProgressBar.__init__(self, parent)
        self.setStyleSheet(DEFAULT_STYLE)
        self.step = 0

    def setValue(self, value):
        QProgressBar.setValue(self, value)
        if value < self.maximum():
            self.setStyleSheet(DEFAULT_STYLE)
        else:
            encrypt_on = xml_encrypt_is_on()
            if encrypt_on is True:
                self.setStyleSheet(COMPLETED_STYLE1)
            else:
                self.setStyleSheet(COMPLETED_STYLE)


class BesDldMainWnd(QMainWindow):
    bar_signal = pyqtSignal(object)
    calibvalue_signal = pyqtSignal(object)
    dldtime_signal = pyqtSignal(object)
    status_signal = pyqtSignal(object)
    btaddr_display_signal = pyqtSignal(object)
    bleaddr_display_signal = pyqtSignal(object)
    dld_succeed_times = 0
    dld_failure_times = 0
    ramrun_path = ''
    flash_bin_path = ''
    flash_boot_bin_path = ''
    Port_list = []
    config_info_display = []
    app_switch = False
    otaboot_switch = False

    def __init__(self, parent=None):
        self.lang_set = get_xmlcfg_language()
        QMainWindow.__init__(self)
        super(BesDldMainWnd, self).__init__(parent)
        if cfg_as_updatetool() is True:
            self.setWindowTitle(str_updatetool_title[self.lang_set])
        else:
            encrypt_on = xml_encrypt_is_on()
            if encrypt_on is True:
                self.setWindowTitle(str_dldtool_encrypt_title[self.lang_set])  # 设置窗口标题
            else:
                self.setWindowTitle(str_dldtool_title[self.lang_set])
            self.setWindowIcon(QIcon('images/download.png'))                     # 设置窗口图标
            self.menu = self.menuBar()                          # 添加菜单栏
            self.operate_menu = self.menu.addMenu(str_operate[self.lang_set])
            self.actionStart_all_menu = self.operate_menu.addAction(str_start_all[self.lang_set])
            self.actionStart_all_menu.setIcon(QIcon('images/start.png'))
            self.actionStart_all_menu.triggered.connect(self.StartAll)
            # self.connect(self.actionStart_all_menu, SIGNAL('triggered()'), self.StartAll)
            self.actionStop_all_menu = self.operate_menu.addAction(str_stop_all[self.lang_set])
            self.actionStop_all_menu.setIcon(QIcon('images/stop.png'))
            self.actionStop_all_menu.triggered.connect(self.StopAll)
            # self.connect(self.actionStop_all_menu, SIGNAL('triggered()'), self.StopAll)
            self.actionQuit = self.operate_menu.addAction(str_exit[self.lang_set])
            self.actionQuit.setIcon(QIcon('images/quit.png'))
            self.actionQuit.triggered.connect(self.close)
            # self.connect(self.actionQuit, SIGNAL('triggered()'), self.close)
            self.config_menu = self.menu.addMenu(str_config[self.lang_set])
            self.actionPort_Setup_menu = self.config_menu.addAction(str_port_config[self.lang_set])
            self.actionPort_Setup_menu.setIcon(QIcon('images/fileset.png'))
            self.actionPort_Setup_menu.triggered.connect(self.set_port_dlg)
            # self.connect(self.actionPort_Setup_menu, SIGNAL('triggered()'), self.set_port_dlg)
            self.action_manager_menu = self.config_menu.addAction(str_bin_path_config[self.lang_set])
            self.action_manager_menu.setIcon(QIcon('images/setup.png'))
            self.action_manager_menu.triggered.connect(self.login)
            # self.connect(self.action_manager_menu, SIGNAL('triggered()'), self.login)
            self.help_menu = self.menu.addMenu(str_help[self.lang_set])
            self.actionUser_manual = self.help_menu.addAction(str_user_manual[self.lang_set])
            self.actionUser_manual.setIcon(QIcon('images/help.png'))
            self.actionUser_manual.triggered.connect(self.manual)
            # self.connect(self.actionUser_manual, SIGNAL('triggered()'), self.manual)
            self.actionAbout = self.help_menu.addAction(str_about[self.lang_set])
            self.actionAbout.setIcon(QIcon('images/about.png'))
            self.actionAbout.triggered.connect(self.about)
            # self.connect(self.actionAbout, SIGNAL('triggered()'), self.about)

            self.statusBar()
            self.toolbar1 = self.addToolBar(str_start_all[self.lang_set])
            self.actionStart_all = self.toolbar1.addAction(str_start_all[self.lang_set])
            self.actionStart_all.setIcon(QIcon('images/start.png'))
            self.actionStart_all.triggered.connect(self.StartAll)
            # self.connect(self.actionStart_all, SIGNAL('triggered()'), self.StartAll)
            self.toolbar2 = self.addToolBar(str_stop_all[self.lang_set])
            self.actionStop_all = self.toolbar2.addAction(str_stop_all[self.lang_set])
            self.actionStop_all.setIcon(QIcon('images/stop.png'))
            self.actionStop_all.triggered.connect(self.StopAll)
            # self.connect(self.actionStop_all, SIGNAL('triggered()'), self.StopAll)
            self.toolbar3 = self.addToolBar(str_exit[self.lang_set])
            self.actionQuit = self.toolbar3.addAction(str_exit[self.lang_set])
            self.actionQuit.setIcon(QIcon('images/quit.png'))
            self.actionQuit.triggered.connect(self.close)
            # self.connect(self.actionQuit, SIGNAL('triggered()'), self.close)
            self.toolbar4 = self.addToolBar(str_port_config[self.lang_set])
            self.actionPort_Setup = self.toolbar4.addAction(str_port_config[self.lang_set])
            self.actionPort_Setup.setIcon(QIcon('images/fileset.png'))
            self.actionPort_Setup.triggered.connect(self.set_port_dlg)
            # self.connect(self.actionPort_Setup, SIGNAL('triggered()'), self.set_port_dlg)
            self.toolbar5 = self.addToolBar(str_bin_path_config[self.lang_set])
            self.action_manager = self.toolbar5.addAction(str_bin_path_config[self.lang_set])
            self.action_manager.setIcon(QIcon('images/setup.png'))
            self.action_manager.triggered.connect(self.login)
            # self.connect(self.action_manager, SIGNAL('triggered()'), self.login)
            self.tableWidget = QTableWidget()
            self.tableWidget.setColumnCount(8)
            self.tableWidget.setRowCount(8)
            self.tableWidget.setMinimumSize(100, 70)
            self.tableWidget.setMinimumHeight(10)
            self.tableWidget.setMinimumWidth(200)
            self.tableWidget.setAutoFillBackground(True)
            self.tableWidget.setUpdatesEnabled(True)
            widget0 = QWidget()
            layout0 = QVBoxLayout()
            layout0.addWidget(self.tableWidget)
            widget0.setLayout(layout0)
            widget0.setUpdatesEnabled(True)
            dock1 = QDockWidget('', self)
            dock1.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
            dock1.setWidget(widget0)
            dock1.setFeatures(QDockWidget.NoDockWidgetFeatures)
            dock1.setMinimumHeight(400)
            self.addDockWidget(Qt.RightDockWidgetArea, dock1)
            self.txtbrws_cfg_info = QTextBrowser()
            self.txtbrws_cfg_info.setEnabled(False)
            self.txtbrws_cfg_info.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            # self.txtbrws_cfg_info.setFixedHeight(50)
            dock2 = QDockWidget('', self)
            dock2.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
            dock2.setWidget(self.txtbrws_cfg_info)
            dock2.setFeatures(QDockWidget.NoDockWidgetFeatures)
            self.addDockWidget(Qt.RightDockWidgetArea, dock2)
            self.txtbrws_result_info = QTextBrowser()
            self.txtbrws_result_info.setEnabled(False)
            self.txtbrws_result_info.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            # self.txtbrws_result_info.setFixedHeight(50)
            if encrypt_on is True:  # 加密模式*******
                font = QFont()
                font.setBold(True)
                font.setPointSize(40)
                self.encrypt_flag = QTextBrowser()
                self.encrypt_flag.setTextColor(QColor(255, 0, 0))
                self.encrypt_flag.setText(str_encrypt_mode[self.lang_set])
                self.encrypt_flag.setFont(font)
                self.encrypt_flag.setAutoFillBackground(True)
                self.encrypt_flag.setEnabled(False)
                self.encrypt_flag.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            self.push_btn_clear = QPushButton(str_clear_count[self.lang_set])
            widget = QWidget()
            bottom_layout = QHBoxLayout()
            if encrypt_on is True:
                bottom_layout.addWidget(self.encrypt_flag)
            bottom_layout.addWidget(self.txtbrws_result_info)
            bottom_layout.addWidget(self.push_btn_clear)
            widget.setLayout(bottom_layout)
            dock3 = QDockWidget('', self)
            dock3.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
            dock3.setWidget(widget)
            dock3.setFeatures(QDockWidget.NoDockWidgetFeatures)
            self.addDockWidget(Qt.RightDockWidgetArea, dock3)
            self.show_productline_cfg_info()
            self.show_dld_result_info()
            self.bar_signal.connect(self.slot_progressbar_update)
            self.calibvalue_signal.connect(self.slot_calibvalue_update)
            self.dldtime_signal.connect(self.slot_dldtime_update)
            self.status_signal.connect(self.slot_status_update)
            self.btaddr_display_signal.connect(self.slot_btaddr_display)
            self.bleaddr_display_signal.connect(self.slot_bleaddr_display)
            self.push_btn_clear.clicked.connect(self.slot_reset_dldresult)
            self.screenwidth = GetSystemMetrics(0)
            self.screenheight = GetSystemMetrics(1)
            self.setTableContents()
            for index in range(0, 8, 1):
                self.dldpipecreate(dld_g.JOBS[index])

        self.setMinimumWidth(1000)
        self.setMinimumHeight(750)

    def getFileCRCText(self, _path):
        crc_ret = dld_g.getFileCRC(_path)
        if crc_ret != 0:
            crc_text = '%08x' % (crc_ret & 4294967295)
            return crc_text
        return 'invalid!'

    def verify_bin_crc(self):
        cfg_app_switch = xml_get_app_switch()
        if cfg_app_switch == '1':
            cfg_verify_crc_switch = xml_get_verifycrc1_switch()
            if cfg_verify_crc_switch == '0':
                return 'success'
            cfg_verify_crc1, cfg_verify_crc2 = xml_get_verify_text()
            if len(cfg_verify_crc1) != 8:
                return 'pls configure verify crc.'
            binfile, otafile = xml_getxmlcfg_burnpath()
            crc_text = self.getFileCRCText(binfile)
            if crc_text.lower() != cfg_verify_crc1.lower():
                # print(crc_text, cfg_verify_crc1)
                return 'crc error'
        cfg_otaboot_switch = xml_get_otaboot_switch()
        if cfg_otaboot_switch == '1':
            cfg_verify_crc_switch = xml_get_verifycrc2_switch()
            if cfg_verify_crc_switch == '0':
                return 'success'
            cfg_verify_crc1, cfg_verify_crc2 = xml_get_verify_text()
            if len(cfg_verify_crc2) != 8:
                return 'pls configure verify crc.'
            binfile, otafile = xml_getxmlcfg_burnpath()
            crc_text = self.getFileCRCText(otafile)
            if crc_text.lower() != cfg_verify_crc2.lower():
                # print(crc_text, cfg_verify_crc2)
                return 'crc error'
        return 'success'

    def verify_bin_md5(self):
        cfg_md5_text = xml_get_verify_text()
        if len(cfg_md5_text) != 32:
            return 'pls configure verify md5.'
        burn_dir = 'burn\\'
        dir_exist_flag = os.path.exists(burn_dir)
        if dir_exist_flag == False:
            return 'pls paste bin(s) under dir burn'
        bin_list = os.listdir(burn_dir)
        for bin_burn in bin_list:
            ext = os.path.splitext(bin_burn)
            if ext[1] == '.bin':
                with open(burn_dir + bin_burn, 'rb') as (f):
                    md5_text = md5(f.read()).hexdigest()
                    # md5_text = md5.new(f.read()).hexdigest()
                    if md5_text == cfg_md5_text:
                        return 'success'
        return 'failure'

    def bes_dldtool_binpath_load(self):
        verify_ret = self.verify_bin_crc()
        if verify_ret != 'success':
            return str_crc_verify_failure[self.lang_set]
        else:
            self.flash_bin_path, self.flash_boot_bin_path = xml_getxmlcfg_burnpath()
            if xml_get_app_switch() == '1':
                self.app_switch = True
                flshbin_exist = os.path.exists(self.flash_bin_path)
                if flshbin_exist is not True:
                    return 'APP file is not exist!'
            else:
                self.app_switch = False
            if xml_get_otaboot_switch() == '1':
                self.otaboot_switch = True
                flashbootbin_exist = os.path.exists(self.flash_boot_bin_path)
                if flashbootbin_exist is not True:
                    return 'OTA BOOT file is not exist!'
            else:
                self.otaboot_switch = False
            chip_version, customer1_enable, custom_bin1_path, customer1_addr, customer2_enable, custom_bin2_path, customer2_addr, customer3_enable, custom_bin3_path, customer3_addr, customer4_enable, custom_bin4_path, customer4_addr = xml_get_customer_info()
            custom_bin1 = ''
            custom_bin2 = ''
            custom_bin3 = ''
            custom_bin4 = ''
            if custom_bin1_path is not None:
                custom_bin1 = str(custom_bin1_path)
            if custom_bin2_path is not None:
                custom_bin2 = str(custom_bin2_path)
            if custom_bin3_path is not None:
                custom_bin3 = str(custom_bin3_path)
            if custom_bin4_path is not None:
                custom_bin4 = str(custom_bin4_path)
            erase_en, erase_len, erase_addr = get_erase_info()
            if self.app_switch == False and self.otaboot_switch == False and custom_bin1 == '' \
                    and custom_bin2 == '' and custom_bin3 == '' and custom_bin4 == '' and erase_en == False:
                return 'Please choose at least a file!'
            if self.app_switch:
                app_bin = self.flash_bin_path
            return 'LOADOK'

    def dldpipecreate(self, job):
        if job['parentconn'] is -1 and job['childconn'] is -1:
            job['parentconn'], job['childconn'] = Pipe()
        if job['parentconn4dldstop'] is -1 and job['childconn4dldstop'] is -1:
            job['parentconn4dldstop'], job['childconn4dldstop'] = Pipe()
        if job['pconn4dldstart'] is -1 and job['cconn4dldstart'] is -1:
            job['pconn4dldstart'], job['cconn4dldstart'] = Pipe()

    def cleandldpipe(self, job):
        if job['parentconn'] is not -1:
            job['parentconn'].close()
            job['parentconn'] = -1
        if job['childconn'] is not -1:
            job['childconn'].close()
            job['childconn'] = -1
        if job['parentconn4dldstop'] is not -1:
            job['parentconn4dldstop'].close()
            job['parentconn4dldstop'] = -1
        if job['childconn4dldstop'] is not -1:
            job['childconn4dldstop'].close()
            job['childconn4dldstop'] = -1
        if job['pconn4dldstart'] is not -1:
            job['pconn4dldstart'].close()
            job['pconn4dldstart'] = -1
        if job['cconn4dldstart'] is not -1:
            job['cconn4dldstart'].close()
            job['cconn4dldstart'] = -1

    def dldfailure_gui_update(self, job):
        status = getSTATE(job)
        status.setText(str_failure[self.lang_set])
        palette = status.palette()
        palette.setColor(status.backgroundRole(), QColor(255, 0, 0))
        status.setPalette(palette)

    def dldsuccess_gui_update(self, job):
        status = getSTATE(job)
        status.setText(str_success[self.lang_set])
        palette = status.palette()
        palette.setColor(status.backgroundRole(), QColor(0, 255, 0))
        status.setPalette(palette)

    def slot_progressbar_update(self, param):
        job = param[0]
        val = param[1]
        progressbar = gui_getprogressbar(job)
        progressbar.setValue(val)

    def slot_calibvalue_update(self, param):
        job = param[0]
        val = param[1]
        calibdisplay = gui_getcalibvalue(job)
        calibdisplay.setText(str(val))

    def slot_dldtime_update(self, param):
        job = param[0]
        timedisplay = param[1]
        gui_time = gui_getTIME(job)
        gui_time.display(timedisplay)

    def slot_status_update(self, param):
        job = param[0]
        string_display = param[1]
        guistatus = getSTATE(job)
        if string_display == 'Idle':
            def task():
                time.sleep(20)
                if string_display == 'Idle':
                    guistatus.setText(str_idle[self.lang_set])
                    temp_palette = guistatus.palette()
                    temp_palette.setColor(guistatus.backgroundRole(), QColor(222, 222, 222))
                    guistatus.setPalette(temp_palette)
            t1 = threading.Thread(target=task, name='Idle reflash')
            t1.start()
        elif string_display == 'Burn Succeed':
            guistatus.setText(str_success[self.lang_set])
            temp_palette = guistatus.palette()
            temp_palette.setColor(guistatus.backgroundRole(), QColor(0, 255, 0))
            guistatus.setPalette(temp_palette)
        elif string_display == 'Test Succeed':
            guistatus.setText(str_success[self.lang_set])
            temp_palette = guistatus.palette()
            temp_palette.setColor(guistatus.backgroundRole(), QColor(0, 255, 0))
            guistatus.setPalette(temp_palette)
        elif string_display == 'Valid':
            self.slot_dld_result_display_update('succeed')
        elif string_display == 'Downloading':
            guistatus.setText(str_burning[self.lang_set])
            temp_palette = guistatus.palette()
            temp_palette.setColor(guistatus.backgroundRole(), QColor(255, 255, 0))
            guistatus.setPalette(temp_palette)
        elif string_display == 'Testing':
            guistatus.setText(str_testing[self.lang_set])
            temp_palette = guistatus.palette()
            temp_palette.setColor(guistatus.backgroundRole(), QColor(255, 255, 0))
            guistatus.setPalette(temp_palette)
        elif string_display == 'password_incorrect':
            guistatus.setText(str_key_format_not_supported[self.lang_set])
            temp_palette = guistatus.palette()
            temp_palette.setColor(guistatus.backgroundRole(), QColor(255, 0, 0))
            guistatus.setPalette(temp_palette)
        elif string_display == 'Failure':
            if param[2] & 4294901760 == 11206656:
                guistatus.setText(str_failure[self.lang_set])
                temp_palette = guistatus.palette()
                temp_palette.setColor(guistatus.backgroundRole(), QColor(255, 0, 0))
                guistatus.setPalette(temp_palette)
        elif string_display == 'Invalid':
            if job['stauts'] != 'stop':
                if param[2] & 4294901760 == 11206656:
                    guistatus.setText(str_failure[self.lang_set])
                    self.slot_dld_result_display_update('failure')
                    self.dldfailure_gui_update(job)
                    temp_palette = guistatus.palette()
                    temp_palette.setColor(guistatus.backgroundRole(), QColor(255, 0, 0))
                    guistatus.setPalette(temp_palette)
            else:
                guistatus.setText(str_stop[self.lang_set])
                temp_palette = guistatus.palette()
                temp_palette.setColor(guistatus.backgroundRole(), QColor(222, 222, 222))
                guistatus.setPalette(temp_palette)
        elif string_display == 'Full':
            self.dld_error_report('Burn all completed, please close tools.')
            self.close()

    def slot_btaddr_display(self, param):
        job = param[0]
        gui_btaddr = gui_get_btaddr_display(job)
        if param[1] != None:
            gui_btaddr.setText(param[1])
        return

    def slot_bleaddr_display(self, param):
        job = param[0]
        gui_bleaddr = gui_get_bleaddr_display(job)
        if param[1] is not None:
            gui_bleaddr.setText(param[1])
        return

    def show_dld_result_info(self):
        count_complete, count_failure = get_dld_result()
        display_text = str_complete_count[self.lang_set] + str(count_complete) + '\n' + str_failure_count[
            self.lang_set] + str(
            count_failure)
        if get_max_burn_num_flag():
            if xml_get_max_burn_num_enable():
                rest_num = get_rest_burn_num()
                total_num = rest_num + count_complete
                display_text = display_text + '\n' + 'Remaining Count:' + str(
                    rest_num) + '\n' + 'Max Burn Count:' + str(total_num)
        self.txtbrws_result_info.setTextColor(QColor(255, 0, 255))
        # self.txtbrws_result_info.setText(display_text.decode('utf-8'))
        self.txtbrws_result_info.setText(display_text)

    def slot_dld_result_display_update(self, result_str):
        if result_str == 'succeed':
            dld_complete_count_increase()
        elif result_str == 'failure':
            dld_failure_count_increase()
        self.show_dld_result_info()

    def slot_reset_dldresult(self):
        reset_dld_result()
        restore_dldresult_to_xml()
        count_complete, count_failure = get_dld_result()
        display_text = str_complete_count[self.lang_set] + str(count_complete) + '\n' + str_failure_count[
            self.lang_set] + str(
            count_failure)
        if get_max_burn_num_flag():
            if xml_get_max_burn_num_enable():
                rest_num = get_rest_burn_num()
                total_num = rest_num + count_complete
                display_text = display_text + '\n' + 'Remaining Count:' + str(
                    rest_num) + '\n' + 'Max Burn Count:' + str(total_num)
        self.txtbrws_result_info.setTextColor(QColor(255, 0, 255))
        self.txtbrws_result_info.setText(display_text)

    def setTableContents(self):
        self.tableWidget.setHorizontalHeaderLabels(
            [str_port_num[self.lang_set], str_com[self.lang_set], str_progress[self.lang_set],
             str_bt_addr[self.lang_set], str_ble_addr[self.lang_set], str_status[self.lang_set],
             str_elapse[self.lang_set],
             str_calib_value[self.lang_set]])
        self.tableWidget.setColumnWidth(0, self.width() / 12)
        self.tableWidget.setColumnWidth(1, self.width() * 1 / 12)
        self.tableWidget.setColumnWidth(2, self.width() * 7.5 / 12)
        self.tableWidget.setColumnWidth(3, self.width() * 2 / 12)
        self.tableWidget.setColumnWidth(4, self.width() * 2 / 12)
        self.tableWidget.setColumnWidth(5, self.width() * 1.5 / 12)
        self.tableWidget.setColumnWidth(6, self.width() * 1.5 / 12)
        self.tableWidget.setColumnWidth(7, self.width() * 1 / 12)
        for i in range(8):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(''))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(''))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(''))
            self.tableWidget.setItem(i, 3, QTableWidgetItem(''))
            self.tableWidget.setItem(i, 4, QTableWidgetItem(''))
            self.tableWidget.setItem(i, 5, QTableWidgetItem(''))
            self.tableWidget.setItem(i, 6, QTableWidgetItem(''))
            self.tableWidget.setItem(i, 7, QTableWidgetItem(''))
            self.tableWidget.setRowHeight(i, self.height() / 12)

        self.tableWidget.horizontalHeader().setStretchLastSection(True)   # 设置拉伸最后一节
        self.tableWidget.setGeometry(1, 1, self.width() * 8 / 10 - 5, self.height() / 2.5)
        self.txtbrws_cfg_info.setGeometry(1, 2 + self.height() / 2.5, self.width() * 8 / 10, self.height() / 12)
        self.txtbrws_result_info.setGeometry(1, 3 + self.height() / 2.5 + self.height() / 14,
                                             self.width() * 7 / 10 - 10, self.height() / 12)
        self.push_btn_clear.setGeometry(self.width() * 7 / 10 - 11, 3 + self.height() / 2.5 + self.height() / 14,
                                        self.width() / 10 + 11, self.height() / 12)

    def about(self):
        dlg = dld_aboutdlg()
        dlg.exec_()

    def manual(self):
        filename = os.getcwd() + '\\user_manual.pdf'
        os.startfile(filename)

    def show_productline_cfg_info(self):
        update_sector_flag = xml_get_update_sector_enable()
        path_text_1, path_text_2 = xml_getxmlcfg_burnpath()
        if path_text_1 is None:
            path_text_1 = ''
        if path_text_2 is None:
            path_text_2 = ''
        if update_sector_flag == '1':
            self.config_info_display = str_bin1_path[self.lang_set] + path_text_1 + '\n' + str_bin2_path[
                self.lang_set] + path_text_2 + '\n' + str_bt_name[self.lang_set] + xml_get_dev_localbtname()
        else:
            self.config_info_display = str_bin1_path[self.lang_set] + path_text_1 + '\n' + str_bin2_path[
                self.lang_set] + path_text_2 + '\n'
        # self.txtbrws_cfg_info.setText(self.config_info_display.decode('utf-8'))
        self.txtbrws_cfg_info.setText(self.config_info_display)
        return

    def login(self):
        dlg = dld_login()
        log_set = dlg.exec_()
        if log_set == 1:
            self.show_productline_cfg_info()

    def set_port_dlg(self):
        dlg = dld_setportdlg()
        if dlg.exec_():
            self.updateport()

    def dld_error_report(self, err_text):
        error_dlg = ErrorReportDlg(err_text)
        error_dlg.exec_()

    def updateport(self):
        global STATE_array
        global TIME_array
        global bar_array
        global calib_value_array
        self.tableWidget.clear()
        self.tableWidget.setHorizontalHeaderLabels(
            [str_port_num[self.lang_set], str_com[self.lang_set], str_progress[self.lang_set],
             str_bt_addr[self.lang_set], str_ble_addr[self.lang_set], str_status[self.lang_set],
             str_elapse[self.lang_set],
             str_calib_value[self.lang_set]])
        for i in range(8):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(''))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(''))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(''))
            self.tableWidget.setItem(i, 3, QTableWidgetItem(''))
            self.tableWidget.setItem(i, 4, QTableWidgetItem(''))
            self.tableWidget.setItem(i, 5, QTableWidgetItem(''))
            self.tableWidget.setItem(i, 6, QTableWidgetItem(''))
            self.tableWidget.setItem(i, 7, QTableWidgetItem(''))

        self.Port_list = []
        self.LineCom = []
        bar_array = []
        STATE_array = []
        TIME_array = []
        calib_value_array = []
        i = 0
        for i, d in enumerate(dld_g.JOBS):
            if i >= dld_g.gettotalportnum():
                break
            index = dld_g.getportNum(i)
            d['portnum'] = index
            index_str = ' %d' % index
            self.Port_list.append(QCheckBox(index_str))
            self.Port_list[i].setChecked(dld_g.getportUsed(i))
            self.Port_list[i].setEnabled(False)
            self.tableWidget.setCellWidget(i, 0, self.Port_list[i])
            self.LineCom.append(QLineEdit('COM%d' % index))
            self.LineCom[i].setEnabled(False)
            self.LineCom[i].setContextMenuPolicy(Qt.NoContextMenu)
            self.LineCom[i].setFocusPolicy(Qt.StrongFocus)
            self.tableWidget.setCellWidget(i, 1, self.LineCom[i])
            bar = XProgressBar(self)
            bar_array.append(bar)
            self.tableWidget.setCellWidget(i, 2, bar)
            bar.setValue(0)
            Btaddress = QLineEdit('00:00:00:00:00:00')
            Btaddress.setEnabled(False)
            dld_g.g_btaddr_display_array[i] = Btaddress
            self.tableWidget.setCellWidget(i, 3, Btaddress)
            Bleaddress = QLineEdit('00:00:00:00:00:00')
            Bleaddress.setEnabled(False)
            dld_g.g_bleaddr_display_array[i] = Bleaddress
            self.tableWidget.setCellWidget(i, 4, Bleaddress)
            State = QLineEdit(str_closed[self.lang_set])
            State.setEnabled(False)
            State.setContextMenuPolicy(Qt.NoContextMenu)
            State.setFocusPolicy(Qt.StrongFocus)
            State.setAutoFillBackground(True)
            p = State.palette()
            p.setColor(State.backgroundRole(), QColor(255, 255, 255))
            State.setPalette(p)
            STATE_array.append(State)
            self.tableWidget.setCellWidget(i, 5, State)
            Time = QLCDNumber()
            Time.setSegmentStyle(QLCDNumber.Filled)
            Time.display('00:00')
            TIME_array.append(Time)
            self.tableWidget.setCellWidget(i, 6, Time)
            Calib_lineedit = QLineEdit('')
            Calib_lineedit.setEnabled(False)
            calib_value_array.append(Calib_lineedit)
            self.tableWidget.setCellWidget(i, 7, Calib_lineedit)

    def btn_stopall_enable(self):
        QAction.setEnabled(self.actionStop_all, True)
        QAction.setEnabled(self.actionStop_all_menu, True)

    def StartAll(self):
        list_len = len(self.Port_list)
        if list_len == 0:
            return
        if get_max_burn_num_flag() == True:
            if xml_get_max_burn_num_enable():
                rest_burn_num = get_rest_burn_num()
                if rest_burn_num <= 0:
                    self.dld_error_report('Burn all completed, please close tools.')
                    self.close()
                    return
        load_text = self.bes_dldtool_binpath_load()
        if load_text != 'LOADOK':
            self.dld_error_report(load_text)
            return
        for index in range(0, list_len, 1):
            if self.Port_list[index].isChecked():
                if dld_g.JOBS[index]['stauts'] is 'run':
                    self.status_signal.emit([dld_g.JOBS[index], 'Idle'])
                if dld_g.JOBS[index]['stauts'] is 'runpending' or dld_g.JOBS[index]['stauts'] is 'done':
                    pass
                elif dld_g.JOBS[index]['stauts'] is 'fail':
                    dld_g.JOBS[index]['stauts'] = 'stop'

        QAction.setEnabled(self.actionStart_all, False)
        QAction.setEnabled(self.action_manager, False)
        QAction.setEnabled(self.actionPort_Setup, False)
        QAction.setEnabled(self.actionStart_all_menu, False)
        QAction.setEnabled(self.action_manager_menu, False)
        QAction.setEnabled(self.actionPort_Setup_menu, False)
        self.bes_dldtool_startall()
        startall_t = Timer(2, self.btn_stopall_enable)
        startall_t.start()

    @staticmethod
    def mkdir_encrypt():
        encrypt_dir = 'bin\\encrypt'
        if not os.path.exists(encrypt_dir):
            os.mkdir(encrypt_dir)

    def mkdir_customer(self):
        customer_dir = 'bin\\customer'
        if os.path.exists(customer_dir):
            shutil.rmtree(customer_dir)
        os.mkdir(customer_dir)

    def secure_mode_bin_prepare(self, index):
        encrypt_bin_path = os.getcwd() + '\\bin\\encrypt\\' + 'app%d.bin' % dld_g.JOBS[index]['ID']
        burn_path_1, _ = xml_getxmlcfg_burnpath()
        shutil.copyfile(burn_path_1, encrypt_bin_path)
        dld_g.JOBS[index]['encrypt_path'] = encrypt_bin_path

    def generate_custom_bin(self, chip_version, bin_path, customer_bin_path, bin_addr):
        shutil.copyfile(bin_path, customer_bin_path)
        bin_addr_interger = int(bin_addr, 16)
        if chip_version == '1000':
            bin_addr_interger = bin_addr_interger + 1811939328
        elif chip_version == '2001' or chip_version == '1501' or chip_version == '2003':
            bin_addr_interger = bin_addr_interger + 738197504
        else:
            bin_addr_interger = bin_addr_interger + 1006632960
        addr_str = dld_g.GlobModule.convert_int_bin(bin_addr_interger)
        fp = open(customer_bin_path, 'ab+')
        fp.write(addr_str)
        fp.close()

    def generate_erase_bin(self, chip_version, erase_bin_path, erase_len, erase_addr):
        erase_len_interger = int(erase_len, 16)
        bin_addr_interger = int(erase_addr, 16)
        if chip_version == '1000':
            bin_addr_interger = bin_addr_interger + 1811939328
        else:
            if chip_version == '2001' or chip_version == '1501' or chip_version == '2003':
                bin_addr_interger = bin_addr_interger + 738197504
            else:
                bin_addr_interger = bin_addr_interger + 1006632960
            addr_str = dld_g.GlobModule.convert_int_bin(bin_addr_interger)
            fp = open(erase_bin_path, 'wb')
            for i in range(0, erase_len_interger):
                bb = struct.pack('B', 255)
                fp.write(bb)

            fp.write(addr_str)
            fp.close()

    def customer_bin_prepare(self):
        self.mkdir_customer()
        customer_bin1_path = ''
        customer_bin2_path = ''
        customer_bin3_path = ''
        customer_bin4_path = ''
        erase_bin_path = ''
        self.custom_bin_list = []
        chip_version, customer1_enable, custom_bin1_path, customer1_addr, customer2_enable, custom_bin2_path, customer2_addr, customer3_enable, custom_bin3_path, customer3_addr, customer4_enable, custom_bin4_path, customer4_addr = xml_get_customer_info()
        if custom_bin1_path is not None:
            bin1_path = str(custom_bin1_path)
            if bin1_path != '':
                bin1_addr = str(customer1_addr)
                customer_bin1_path = os.getcwd() + '\\bin\\customer\\customer1.bin'
                self.generate_custom_bin(chip_version, bin1_path, customer_bin1_path, bin1_addr)
        if custom_bin2_path is not None:
            bin2_path = str(custom_bin2_path)
            if bin2_path != '' and bin2_path != None:
                bin2_addr = str(customer2_addr)
                customer_bin2_path = os.getcwd() + '\\bin\\customer\\customer2.bin'
                self.generate_custom_bin(chip_version, bin2_path, customer_bin2_path, bin2_addr)
        if custom_bin3_path is not None:
            bin3_path = str(custom_bin3_path)
            if bin3_path != '' and bin3_path != None:
                bin3_addr = str(customer3_addr)
                customer_bin3_path = os.getcwd() + '\\bin\\customer\\customer3.bin'
                self.generate_custom_bin(chip_version, bin3_path, customer_bin3_path, bin3_addr)
        if custom_bin4_path is not None:
            bin4_path = str(custom_bin4_path)
            if bin4_path != '' and bin4_path is not None:
                bin4_addr = str(customer4_addr)
                customer_bin4_path = os.getcwd() + '\\bin\\customer\\customer4.bin'
                self.generate_custom_bin(chip_version, bin4_path, customer_bin4_path, bin4_addr)
        erase_en, erase_len, erase_addr = get_erase_info()
        if erase_en:
            erase_bin_path = os.getcwd() + '\\bin\\customer\\erase.bin'
            self.generate_erase_bin(chip_version, erase_bin_path, erase_len, erase_addr)
        self.custom_bin_list = [erase_bin_path, customer_bin1_path, customer_bin2_path, customer_bin3_path,
                                customer_bin4_path]
        return

    def bes_dldtool_startall(self):
        self.customer_bin_prepare()
        encrypt_on = xml_encrypt_is_on()
        list_len = len(self.Port_list)
        if list_len == 0:
            return
        for index in range(0, list_len, 1):
            if self.Port_list[index].isChecked():
                if dld_g.JOBS[index]['stauts'] is 'runpending' or dld_g.JOBS[index]['stauts'] is 'done':
                    pass
                else:
                    if encrypt_on is True:
                        BesDldMainWnd.mkdir_encrypt()
                        self.secure_mode_bin_prepare(index)
                    self.bes_dldtool_gui_reset(dld_g.JOBS[index])
                    self.bes_dldtool_mainprocess_thrd_start(dld_g.JOBS[index], index)
                    if not xml_getxmlcfg_is_fctrmdonly():
                        factory_bin_name = dld_g.JOBS[index]['factorybin']
                        bt_addr_dis, ble_addr_dis, calib_value, sn = dld_sector_gen(factory_bin_name, True)
                        dld_g.JOBS[index]['bt_addr_pack'] = struct.pack('<6B', bt_addr_dis[5], bt_addr_dis[4],
                                                                        bt_addr_dis[3], bt_addr_dis[2], bt_addr_dis[1],
                                                                        bt_addr_dis[0])
                        dld_g.JOBS[index]['btaddrtext'] = '%02X:%02X:%02X:%02X:%02X:%02X' % (bt_addr_dis[0],
                                                                                             bt_addr_dis[1],
                                                                                             bt_addr_dis[2],
                                                                                             bt_addr_dis[3],
                                                                                             bt_addr_dis[4],
                                                                                             bt_addr_dis[5])
                        dld_g.JOBS[index]['bleaddrtext'] = '%02X:%02X:%02X:%02X:%02X:%02X' % (ble_addr_dis[0],
                                                                                              ble_addr_dis[1],
                                                                                              ble_addr_dis[2],
                                                                                              ble_addr_dis[3],
                                                                                              ble_addr_dis[4],
                                                                                              ble_addr_dis[5])
                        dld_g.JOBS[index]['sntext'] = sn
                        write_cfg_log(dld_g.JOBS[index]['btaddrtext'], dld_g.JOBS[index]['bleaddrtext'], calib_value,
                                      dld_g.JOBS[index]['sntext'])
                        calibdisplay = gui_getcalibvalue(dld_g.JOBS[index])
                        if xml_get_update_calib_enable() == 0 or xml_get_update_sector_enable() == '0':
                            calibdisplay.setText('')
                        else:
                            calibdisplay.setText(str(calib_value))
                    else:
                        write_cfg_log('0', '0', 0, '0')

        for each_i in range(0, list_len, 1):
            if self.Port_list[each_i].isChecked():
                self.jobstart(dld_g.JOBS[each_i], each_i)

    def btn_allstart_enable(self):
        QAction.setEnabled(self.actionStart_all, True)
        QAction.setEnabled(self.action_manager, True)
        QAction.setEnabled(self.actionPort_Setup, True)
        QAction.setEnabled(self.actionStart_all_menu, True)
        QAction.setEnabled(self.action_manager_menu, True)
        QAction.setEnabled(self.actionPort_Setup_menu, True)

    def all_job_is_stop(self):
        if not (dld_g.JOBS[0]['stauts'] != 'stop' or not (dld_g.JOBS[1]['stauts'] == 'stop') or not (
                dld_g.JOBS[2]['stauts'] == 'stop')) and (dld_g.JOBS[3]['stauts'] == 'stop') \
                and dld_g.JOBS[4]['stauts'] == 'stop' and dld_g.JOBS[5]['stauts'] == 'stop' \
                and dld_g.JOBS[6]['stauts'] == 'stop' and dld_g.JOBS[7]['stauts'] == 'stop':
            return 'YES'
        return 'NO'

    def StopAll(self):
        if 'YES' == self.all_job_is_stop():
            return
        QAction.setEnabled(self.actionStop_all, False)
        self.bes_dldtool_stop()
        stopall_t = Timer(3, self.btn_allstart_enable)
        stopall_t.start()

    def update_bar_info(self, bar):
        if bar.step <= 100:
            bar.setValue(bar.step)

    def update_time_info(self, Time):
        Time.display(Time.str)

    def bes_dldtool_gui_reset(self, d):
        # self.jobSTATE = getSTATE(d)
        # self.guitime = gui_getTIME(d)
        if d['stauts'] == 'stop':
            d['stauts'] = 'runpending'
            self.status_signal.emit([d, 'Idle'])

    def mainp_notify_subp_startburn(self):
        msg_list = ['MSG_DLD_START', xml_getxmlcfg_is_fctrmdonly(), burn_appota_only(), get_baudrate()]
        self.job['pconn4dldstart'].send(msg_list)
        self.job['parentconn4dldstop'].send(['MSG_SYNC_ENCRPYT_DATA', self.job['bt_addr_pack']])

    def bes_dldtool_mainprocess_thrd_start(self, job, index):
        monitorthrd = dld_g.getmonitorthrd(index)
        if dld_g.g_monitorthrd_array[index] is not None:
            if dld_g.g_monitorthrd_array[index].isAlive():
                return
        job['semaindex'] = index
        monitor_sema = dld_g.getsema(job['semaindex'])
        if monitor_sema is None:
            monitor_sema = threading.Semaphore(0)
            dld_g.setsema(index, monitor_sema)
        monitor_thrd = DldProgressMonitor(job, self.bar_signal, self.status_signal, self.dldtime_signal, monitor_sema,
                                          self.btaddr_display_signal, self.bleaddr_display_signal,
                                          self.calibvalue_signal)
        monitor_thrd.start()
        dld_g.setmonitorthrd(index, monitor_thrd)
        return

    # def bes_dldtool_mainprocess_monitorthrd_end(self):
    #     if JOBS[0]['stauts'] is not 'stop':
    #         return
    #     else:
    #         if len(g_monitorthrd_array) > 0:
    #             for i, thrd in enumerate(g_monitorthrd_array):
    #                 monitorthrdsema = gui_getsema(i)
    #                 if monitorthrdsema is not None:
    #                     monitorthrdsema.release()
    #                 g_monitorthrd_array[i] = None
    #
    #         return
    #  debug!!!!  这里的monitorthrd_array 不知道哪里来的。该段代码未启用  monitorthrd监控线程？？？？

    def doAction(self):
        pass

    def jobstart(self, d, index):
        self.job = d
        self.subproc = None
        cfg_as_update = cfg_as_updatetool()
        encrypt_on = xml_encrypt_is_on()
        erase_whole = xml_get_erasewhole_switch()
        if self.job['stauts'] == 'runpending':
            self.job['stauts'] = 'run'
            gen_btaddr_enable = xml_get_update_sector_enable()
            connector_switch = xml_get_connector_cfg()
            calib_switch = xml_get_calibrate_cfg()
            Customized_enable = xml_get_update_Customized_enable()
            Customized_Addr = xml_get_update_Customized_Addr()
            if xml_get_update_sector_enable() == '0':
                burn_field_enable_value = 64 + 32 + 16 + 8 + 4 + 2 + 1
            else:
                burn_field_enable_value = (xml_get_update_sn_enable() << 6) + (xml_get_update_btaddr_enable() << 5) + (
                        xml_get_update_btname_enable() << 4) + (xml_get_update_bleaddr_enable() << 3) + (
                                                  xml_get_update_blename_enable() << 2) + (
                                                  xml_get_update_conaddr_enable() << 1) + xml_get_update_calib_enable()
            if encrypt_on is True:
                ffile = dld_g.JOBS[index]['encrypt_path']
            else:
                ffile = str(self.flash_bin_path)
                fbfile = str(self.flash_boot_bin_path)
            self.mainp_notify_subp_startburn()
            self.subproc = DldProcess(self.job, str(self.ramrun_path), ffile, fbfile,
                                      self.app_switch, self.otaboot_switch, gen_btaddr_enable, connector_switch,
                                      calib_switch, cfg_as_update, burn_field_enable_value, self.custom_bin_list,
                                      encrypt_on, erase_whole, Customized_enable, Customized_Addr)
            self.subproc.start()
            time.sleep(0.05)
            monit_thrd_sema = dld_g.getsema(self.job['semaindex'])
            monit_thrd_sema.release()
        return

    def closeEvent(self, event):
        reply = QMessageBox.question(self, str_quit[self.lang_set], str_quit_message[self.lang_set],
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.gen_unuse_addr()
            restore_dldresult_to_xml()
            for i, d in enumerate(dld_g.JOBS):
                self.clean_alive_threads(d, i)

            event.accept()
        elif reply == QMessageBox.No:
            event.ignore()

    def clean_alive_threads(self, job, index):
        job['stauts'] = 'leaving'
        if job['parentconn4dldstop'] is not -1:
            job['parentconn4dldstop'].send(['MSG_DLD_STOP'])
        if job['pconn4dldstart'] is not -1:
            job['pconn4dldstart'].send('MSG_DLD_END')
        if job['monitorthrdindex'] is not -1:
            self.monitor_thrd_id = gui_getmonitorthrd(job)
            self.monitor_thrd_sema = dld_g.getsema(job['semaindex'])
            if self.monitor_thrd_id.isAlive():
                if self.monitor_thrd_sema is not None:
                    self.monitor_thrd_sema.release()
        return

    def bes_dldtool_ajob_stop(self, index, ajob):
        while ajob['stauts'] is 'runpending':
            bes_trace('waiting')

        bes_trace('bes_dldtool_ajob_stop, job status is %s\n' % ajob['stauts'])
        ajob['stauts'] = 'stop'
        if ajob['parentconn4dldstop'] is not -1:
            ajob['parentconn4dldstop'].send(['MSG_DLD_STOP'])
        if ajob['pconn4dldstart'] is not -1:
            ajob['pconn4dldstart'].send('MSG_DLD_END')
        if ajob['monitorthrdindex'] is not -1:
            self.monitor_thrd_id = gui_getmonitorthrd(ajob)
            self.monitor_thrd_sema = dld_g.getsema(ajob['semaindex'])
            if self.monitor_thrd_id.isAlive():
                if self.monitor_thrd_sema is not None:
                    self.monitor_thrd_sema.release()
        progressbar = gui_getprogressbar(ajob)
        progressbar.setValue(0)
        gui_status = getSTATE(ajob)
        gui_status.setText(str_stop[self.lang_set])
        temp_palette = gui_status.palette()
        temp_palette.setColor(gui_status.backgroundRole(), QColor(222, 222, 222))
        gui_status.setPalette(temp_palette)
        return

    def bes_dldtool_stop(self):
        self.gen_unuse_addr()
        for i, d in enumerate(dld_g.JOBS):
            if d['stauts'] is not 'stop':
                self.bes_dldtool_ajob_stop(i, d)

        restore_dldresult_to_xml()

    def gen_unuse_addr(self):
        using_bt_addr = get_using_bt_addr()
        failed_bt_addr = xml_get_failed_bt_addr()
        for i in range(0, len(using_bt_addr)):
            failed_bt_addr.append(using_bt_addr[i])

        using_bt_addr = []
        failed_bt_addr = list(set(failed_bt_addr))
        xml_set_failed_bt_addr(failed_bt_addr)
        using_ble_addr = get_using_ble_addr()
        failed_ble_addr = xml_get_failed_ble_addr()
        for i in range(0, len(using_ble_addr)):
            failed_ble_addr.append(using_ble_addr[i])

        using_ble_addr = []
        failed_ble_addr = list(set(failed_ble_addr))
        xml_set_failed_ble_addr(failed_ble_addr)
        xml_doc_write()
