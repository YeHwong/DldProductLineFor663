#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2023-02-17 14:26:40
# @File: dld_main.py
# @Author: YeHwong
# @Email: 598316810@qq.com
# @Version ：1.0.0
import sys
import multiprocessing as mp
from ctypes import c_char

from PyQt5.QtWidgets import QApplication

import dld_global as dld_g
from dld_mainwnd import BesDldMainWnd
from dld_xml_operate import xml_dev_local_name_write_back, xml_doc_parse, xml_get_encrypt_on,\
    xml_mod_for_encrypt_mode, xml_getxmlcfg_burnpath
from cfg_json_parse import config_json_parse
from error_report import ErrorReportDlg
from win32api import GetLastError
from winerror import ERROR_ALREADY_EXISTS


class wt_dld_tool_app_instance:
    def __init__(self):
        from win32event import CreateMutex
        self.mutexName = '%s.%s' % (dld_g.G_COMPANY_NAME, dld_g.G_APP_NAME)
        self.myMutex = CreateMutex(None, False, self.mutexName)
        self.lastErr = GetLastError()

    def app_is_alive(self):
        if self.lastErr == ERROR_ALREADY_EXISTS:
            return True
        else:
            return False


if __name__ == '__main__':
    mp.freeze_support()     # Windows环境下添加multiprocessing多进程支持
    bes_dld_tool_app = QApplication(sys.argv)
    dld_g.initglobal()      # 初始化全局变量
    if xml_get_encrypt_on():
        xml_mod_for_encrypt_mode()
    parse_val = xml_doc_parse()
    if parse_val == 'xmlcfgok':
        if not config_json_parse():
            error_dlg = ErrorReportDlg('json parse fail')
            error_dlg.exec_()
        else:
            burn_path_text_1, burn_path_text_2 = xml_getxmlcfg_burnpath()
            if burn_path_text_1 is not None:
                dld_g.get_dlddll().handle_buildinfo_to_extend(burn_path_text_1)
                buf = (c_char * 249)()
                build_info_bt_name_len = dld_g.get_dlddll().get_build_info_bt_name(buf)
                if build_info_bt_name_len is not 0:
                    name_str = ''
                    for i in range(build_info_bt_name_len):
                        name_str = name_str + str(buf[i])
                    xml_dev_local_name_write_back(name_str)
            bes_dld_tool_window = BesDldMainWnd()
            bes_dld_tool_window.show()
            bes_dld_tool_app.exit(bes_dld_tool_app.exec_())
    else:
        error_dlg = ErrorReportDlg(parse_val)
        error_dlg.exec_()
