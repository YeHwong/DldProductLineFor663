#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2023-02-17 14:26:18
# @File: dld_productlinecfg.py
# @Author: YeHwong
# @Email: 598316810@qq.com
# @Version ：1.1.0
# 修复文件选择后闪退BUG


from PyQt5 import uic
from PyQt5.QtWidgets import QFileDialog, QDialog

from error_report import ErrorReportDlg
from dld_string_res import *
from cfg_json_parse import get_max_burn_num_flag
from dld_xml_operate import *

lang_set = get_xmlcfg_language()
if lang_set == 'en':
    productline_cfg_ui = 'productline_config_en.ui'
else:
    productline_cfg_ui = 'productline_config.ui'
Ui_productlinecfg_window, QtBaseClass = uic.loadUiType(productline_cfg_ui)


class ProductlineCfg(QDialog, Ui_productlinecfg_window):

    def __init__(self):
        QDialog.__init__(self)
        Ui_productlinecfg_window.__init__(self)
        lang_set = get_xmlcfg_language()
        self.setupUi(self)
        self.gen_addr_type_filter = str_btaddr_filter[lang_set]
        self.gen_addr_type_grow = str_btaddr_add1[lang_set]
        self.gen_addr_type_fixed = str_btaddr_fixed[lang_set]
        self.gen_addr_raise_2 = str_btaddr_Raise_2[lang_set]
        self.saveed_data_list = []
        self.gen_addr_type_list = [self.gen_addr_type_filter, self.gen_addr_type_grow, self.gen_addr_raise_2,
                                   self.gen_addr_type_fixed]
        self.combbx_addr_gen_type.addItems(self.gen_addr_type_list)
        self.gen_sn_type_grow = str_sn_add[lang_set]
        self.gen_sn_type_fixed = str_sn_fixed[lang_set]
        self.gen_sn_type_list = [self.gen_sn_type_grow, self.gen_sn_type_fixed]
        self.combbx_sn_gen_type.addItems(self.gen_sn_type_list)
        self.chipver_list = ['1000', '2000', '2300', '1400', '2300p', '2300a', '1501', '2001',
                             '1305', '2003']
        self.comboBox_chipver.addItems(self.chipver_list)
        self.chipver_index_dic = {'1000': 0, '2000': 1, '2300': 2, '1400': 3, '2300p': 4, '2300a': 5, '1501': 6,
                                  '2001': 7, '1305': 8, '2003': 9}
        self.binpath_1 = None
        self.binpath_2 = None
        self.checkbox_burn_switch.clicked.connect(self.burn_switch_slot)
        self.checkbox_update_sector.clicked.connect(self.update_sector_slot)
        if cfg_as_updatetool() is False:
            self.checkbox_factory_switch.clicked.connect(self.factory_switch_slot)
        else:
            self.checkbox_factory_switch.setVisible(False)
            self.groupBox_factorymode_setting.setVisible(False)
        self.push_btn_save.clicked.connect(self.factoryline_configure_save_slot)
        self.push_btn_exit.clicked.connect(self.close)
        self.push_btn_browse_1.clicked.connect(self.browse_bin_path_1)
        self.push_btn_browse_2.clicked.connect(self.browse_bin_path_2)
        self.btn_custom_bin_browse1.clicked.connect(self.browse_custom_bin1)
        self.btn_custom_bin_browse2.clicked.connect(self.browse_custom_bin2)
        self.btn_custom_bin_browse3.clicked.connect(self.browse_custom_bin3)
        self.btn_custom_bin_browse4.clicked.connect(self.browse_custom_bin4)
        self.chkbox_app.clicked.connect(self.showappbrowse)
        self.chkbox_boot.clicked.connect(self.showbootbrowse)
        self.chkbox_filename.clicked.connect(self.setbtname)
        self.chkbox_appcrc.clicked.connect(self.showappcrc)
        self.chkbox_bootcrc.clicked.connect(self.showbootcrc)
        self.chkbox_custom_bin1.clicked.connect(self.en_disn_able_custom_bin1_widgets)
        self.chkbox_custom_bin2.clicked.connect(self.en_disn_able_custom_bin2_widgets)
        self.chkbox_custom_bin3.clicked.connect(self.en_disn_able_custom_bin3_widgets)
        self.chkbox_custom_bin4.clicked.connect(self.en_disn_able_custom_bin4_widgets)
        self.checkBox_btaddr.stateChanged.connect(self.checkBox_btaddr_slot)
        self.checkBox_btname.stateChanged.connect(self.checkBox_btname_slot)
        self.checkBox_bleaddr.stateChanged.connect(self.checkBox_bleaddr_slot)
        self.checkBox_conaddr.stateChanged.connect(self.checkBox_conaddr_slot)
        self.checkBox_calib.stateChanged.connect(self.checkBox_calib_slot)
        self.checkBox_blename.stateChanged.connect(self.checkBox_blename_slot)
        self.combbx_addr_gen_type.currentIndexChanged.connect(self.combBox_addr_gen_type_slot)
        # self.connect(self.checkBox_btaddr, SIGNAL('stateChanged (int)'), self.checkBox_btaddr_slot)
        # self.connect(self.checkBox_btname, SIGNAL('stateChanged (int)'), self.checkBox_btname_slot)
        # self.connect(self.checkBox_bleaddr, SIGNAL('stateChanged (int)'), self.checkBox_bleaddr_slot)
        # self.connect(self.checkBox_conaddr, SIGNAL('stateChanged (int)'), self.checkBox_conaddr_slot)
        # self.connect(self.checkBox_calib, SIGNAL('stateChanged (int)'), self.checkBox_calib_slot)
        # self.connect(self.checkBox_blename, SIGNAL('stateChanged (int)'), self.checkBox_blename_slot)
        # self.connect(self.combbx_addr_gen_type, SIGNAL('currentIndexChanged(int)'), self.combBox_addr_gen_type_slot)
        self.custom_bin1_path = ''
        self.custom_bin2_path = ''
        self.custom_bin3_path = ''
        self.custom_bin4_path = ''
        self.init_productline_config_dialog()
        if xml_encrypt_is_on():
            self.init_productline_encry_mode()
        if get_dlddll().get_version() < 2:
            self.label_15.setVisible(True)
            self.lineedit_blename.setVisible(True)
            self.checkBox_blename.setVisible(True)
        else:
            self.label_15.setVisible(True)
            self.lineedit_blename.setVisible(True)
            self.checkBox_blename.setVisible(True)
        chiptypestr = ''
        buf = (c_char * 20)()
        chiptype_len = get_dlddll().get_chiptype_value(buf)
        if chiptype_len is not 0:
            for i in range(chiptype_len):
                chiptypestr = chiptypestr + str(buf[i])

        if chiptypestr == '1400' or chiptypestr == '1501':
            self.label_14.setText('Default Calib Value(20~511):')
        else:
            self.label_14.setText('Default Calib Value(20~235):')
        self.setburnitem(burn_appota_only())
        self.checkBox_sn.setVisible(False)
        self.label_18.setVisible(False)
        self.combbx_sn_gen_type.setVisible(False)
        self.label_19.setVisible(False)
        self.lineedit_sn.setVisible(False)
        if not get_max_burn_num_flag():
            self.checkBox_burnnum.setVisible(False)
            self.lineedit_maxburnnum.setVisible(False)
        self.checkbox_erase_whole.setVisible(False)
        self.label_21.setVisible(False)
        return

    def setburnitem(self, appota_only):
        if appota_only:
            self.checkbox_update_sector.setEnabled(False)
            self.chkbox_filename.setEnabled(False)
            self.chkbox_custom_bin1.setEnabled(False)
            self.chkbox_custom_bin2.setEnabled(False)
            self.chkbox_custom_bin3.setEnabled(False)
            self.chkbox_custom_bin4.setEnabled(False)
            self.checkbox_factory_switch.setEnabled(False)
            self.checkbox_update_sector.setChecked(False)
            self.groupBox.setEnabled(False)
            self.chkbox_filename.setChecked(False)
            self.chkbox_custom_bin1.setChecked(False)
            self.chkbox_custom_bin2.setChecked(False)
            self.chkbox_custom_bin3.setChecked(False)
            self.chkbox_custom_bin4.setChecked(False)
            self.checkbox_factory_switch.setChecked(False)
            self.checkbox_erase_whole.setEnabled(False)
            self.checkbox_erase_whole.setChecked(False)
        else:
            self.checkbox_update_sector.setEnabled(True)
            self.chkbox_filename.setEnabled(True)
            self.chkbox_custom_bin1.setEnabled(True)
            self.chkbox_custom_bin2.setEnabled(True)
            self.chkbox_custom_bin3.setEnabled(True)
            self.chkbox_custom_bin4.setEnabled(True)
            self.checkbox_factory_switch.setEnabled(True)
            self.checkbox_erase_whole.setEnabled(True)

    def init_productline_encry_mode(self):
        self.checkbox_update_sector.setChecked(True)
        self.checkbox_update_sector.setEnabled(False)
        self.combbx_addr_gen_type.setCurrentIndex(1)
        self.combbx_addr_gen_type.setEnabled(False)
        self.checkBox_btaddr.setChecked(True)
        self.checkBox_btname.setChecked(True)
        self.checkBox_bleaddr.setChecked(True)
        self.checkBox_conaddr.setChecked(True)
        self.checkBox_calib.setChecked(True)
        self.checkBox_blename.setChecked(True)
        self.checkBox_btaddr.setVisible(False)
        self.checkBox_btname.setVisible(False)
        self.checkBox_bleaddr.setVisible(False)
        self.checkBox_conaddr.setVisible(False)
        self.checkBox_calib.setVisible(False)
        self.checkBox_blename.setVisible(False)

    def combBox_addr_gen_type_slot(self):
        if self.combbx_addr_gen_type.currentIndex() != 3:
            self.checkBox_burnnum.setChecked(True)
            self.lineedit_maxburnnum.setEnabled(True)
            self.lineedit_maxburnnum.setText('1')
        else:
            self.checkBox_burnnum.setEnabled(False)
            self.lineedit_maxburnnum.setEnabled(False)
            self.checkBox_burnnum.setChecked(False)
            self.lineedit_maxburnnum.setText('0')

    def checkBox_btaddr_slot(self):
        if self.checkBox_btaddr.isChecked():
            self.label.setEnabled(True)
            self.label_2.setEnabled(True)
            self.label_3.setEnabled(True)
            self.label_4.setEnabled(True)
            self.lineedit_btnap.setEnabled(True)
            self.lineedit_btuap.setEnabled(True)
            self.lineedit_btlap.setEnabled(True)
        else:
            self.label.setEnabled(False)
            self.label_2.setEnabled(False)
            self.label_3.setEnabled(False)
            self.label_4.setEnabled(False)
            self.lineedit_btnap.setEnabled(False)
            self.lineedit_btuap.setEnabled(False)
            self.lineedit_btlap.setEnabled(False)

    def checkBox_btname_slot(self):
        if self.checkBox_btname.isChecked():
            self.label_5.setEnabled(True)
            self.lineedit_btname.setEnabled(True)
        else:
            self.label_5.setEnabled(False)
            self.lineedit_btname.setEnabled(False)

    def checkBox_blename_slot(self):
        if self.checkBox_blename.isChecked():
            self.label_15.setEnabled(True)
            self.lineedit_blename.setEnabled(True)
        else:
            self.label_15.setEnabled(False)
            self.lineedit_blename.setEnabled(False)

    def checkBox_bleaddr_slot(self):
        if self.checkBox_bleaddr.isChecked():
            self.label_6.setEnabled(True)
            self.label_7.setEnabled(True)
            self.label_8.setEnabled(True)
            self.label_9.setEnabled(True)
            self.lineedit_blenap.setEnabled(True)
            self.lineedit_bleuap.setEnabled(True)
            self.lineedit_blelap.setEnabled(True)
        else:
            self.label_6.setEnabled(False)
            self.label_7.setEnabled(False)
            self.label_8.setEnabled(False)
            self.label_9.setEnabled(False)
            self.lineedit_blenap.setEnabled(False)
            self.lineedit_bleuap.setEnabled(False)
            self.lineedit_blelap.setEnabled(False)

    def checkBox_conaddr_slot(self):
        if self.checkBox_conaddr.isChecked():
            self.label_10.setEnabled(True)
            self.label_11.setEnabled(True)
            self.label_12.setEnabled(True)
            self.label_13.setEnabled(True)
            self.lineedit_connectornap.setEnabled(True)
            self.lineedit_connectoruap.setEnabled(True)
            self.lineedit_connectorlap.setEnabled(True)
        else:
            self.label_10.setEnabled(False)
            self.label_11.setEnabled(False)
            self.label_12.setEnabled(False)
            self.label_13.setEnabled(False)
            self.lineedit_connectornap.setEnabled(False)
            self.lineedit_connectoruap.setEnabled(False)
            self.lineedit_connectorlap.setEnabled(False)

    def checkBox_calib_slot(self):
        if self.checkBox_calib.isChecked():
            self.label_14.setEnabled(True)
            self.lineedit_default_calibval.setEnabled(True)
        else:
            self.label_14.setEnabled(False)
            self.lineedit_default_calibval.setEnabled(False)

    def update_bt_name_text(self, local_name, disable_flag):
        """update bt name text"""
        self.lineedit_btname.setText(local_name)
        if disable_flag is True:
            self.lineedit_btname.setEnabled(False)

    def browse_bin_path_1(self):
        self.binpath_1 = QFileDialog.getOpenFileName(self, 'Select Flash File', '', '*.bin')
        # print(f'binpath_1:{self.binpath_1}')
        if len(self.binpath_1) != 0:
            get_dlddll().handle_buildinfo_to_extend(str(self.binpath_1))
            buf = (c_char * 249)()
            buildinfo_bt_name_len = get_dlddll().get_build_info_bt_name(buf)
            if buildinfo_bt_name_len is not 0:
                namestr = ''
                for i in range(buildinfo_bt_name_len):
                    namestr = namestr + str(buf[i])

                self.update_bt_name_text(namestr, True)
            # print(self.binpath_1)
            self.lineedit_bin_path_1.setText(self.binpath_1[0])
            if self.chkbox_filename.isChecked() and self.checkbox_update_sector.isChecked():
                strlist = self.binpath_1.split('/')
                strlen = len(strlist)
                filename = strlist[strlen - 1].split('.')[0]
                self.lineedit_btname.setText(filename)
            if get_dlddll().get_version() < 2:
                self.label_15.setVisible(False)
                self.lineedit_blename.setVisible(False)
                self.checkBox_blename.setVisible(False)
            else:
                self.label_15.setVisible(True)
                self.lineedit_blename.setVisible(True)
                self.checkBox_blename.setVisible(True)
            chiptypestr = ''
            buf = (c_char * 20)()
            chiptype_len = get_dlddll().get_chiptype_value(buf)
            if chiptype_len is not 0:
                for i in range(chiptype_len):
                    chiptypestr = chiptypestr + str(buf[i])

            if chiptypestr == '1400' or chiptypestr == '1501':
                self.label_14.setText('Default Calib Value(20~511):')
            else:
                self.label_14.setText('Default Calib Value(20~235):')
            cfg_calib_val = xml_getxmlcfg_default_calib_value()
            cfg_calib_text = str('%d' % cfg_calib_val)
            self.lineedit_default_calibval.setText(cfg_calib_text)
            try:
                self.comboBox_chipver.setCurrentIndex(self.chipver_index_dic[chiptypestr])
            except:
                pass

    def browse_custom_bin1(self):
        self.custom_bin1_path = QFileDialog.getOpenFileName(self, 'Selecct bin', '', '*.bin')
        if len(self.custom_bin1_path) == 0:
            return
        print(self.custom_bin1_path)
        self.lineedit_custom_bin1.setText(self.custom_bin1_path[0])    # BIN修复文件选择后闪退BUG

    def browse_custom_bin2(self):
        self.custom_bin2_path = QFileDialog.getOpenFileName(self, 'Selecct bin', '', '*.bin')
        if len(self.custom_bin2_path) == 0:
            return
        self.lineedit_custom_bin2.setText(self.custom_bin2_path[0])

    def browse_custom_bin3(self):
        self.custom_bin3_path = QFileDialog.getOpenFileName(self, 'Selecct bin', '', '*.bin')
        if len(self.custom_bin3_path) == 0:
            return
        self.lineedit_custom_bin3.setText(self.custom_bin3_path[0])

    def browse_custom_bin4(self):
        self.custom_bin4_path = QFileDialog.getOpenFileName(self, 'Selecct bin', '', '*.bin')
        if len(self.custom_bin4_path) == 0:
            return
        self.lineedit_custom_bin4.setText(self.custom_bin4_path[0])

    def browse_bin_path_2(self):
        """
            获取OTA_BOOT文件的地址信息

        """
        self.binpath_2 = QFileDialog.getOpenFileName(self, 'Select Flash File', '', '*.bin')
        if len(self.binpath_2) != 0:
            self.lineedit_bin_path_2.setText(self.binpath_2[0])
            if not self.chkbox_app.isChecked() and self.chkbox_filename.isChecked() and self.checkbox_update_sector.isChecked():
                strlist = self.binpath_2.split('/')
                strlen = len(strlist)
                filename = strlist[strlen - 1].split('.')[0]
                self.lineedit_btname.setText(filename)

    def custom_bin_widget_gui_init(self):
        """custom bin widget gui init"""
        chip_version, customer1_enable, customer1_path, customer1_addr, customer2_enable, customer2_path, customer2_addr, customer3_enable, customer3_path, customer3_addr, customer4_enable, customer4_path, customer4_addr = xml_get_customer_info()
        try:
            self.comboBox_chipver.setCurrentIndex(self.chipver_index_dic[chip_version])
        except Exception as e:
            print(e)

        if customer1_enable == '1':
            self.chkbox_custom_bin1.setChecked(True)
            self.lineedit_custom_bin1.setText(str(customer1_path))
            self.lineEdit_addr1.setText(str(customer1_addr))
            self.btn_custom_bin_browse1.setEnabled(True)
            self.label_addr1.setEnabled(True)
            self.lineEdit_addr1.setEnabled(True)
        else:
            self.label_custom_bin1.setEnabled(False)
            self.chkbox_custom_bin1.setChecked(False)
            self.btn_custom_bin_browse1.setEnabled(False)
            self.label_addr1.setEnabled(False)
            self.lineEdit_addr1.setEnabled(False)
        if customer2_enable == '1':
            self.chkbox_custom_bin2.setChecked(True)
            self.lineedit_custom_bin2.setText(str(customer2_path))
            self.lineEdit_addr2.setText(str(customer2_addr))
            self.btn_custom_bin_browse2.setEnabled(True)
            self.label_addr2.setEnabled(True)
            self.lineEdit_addr2.setEnabled(True)
        else:
            self.label_custom_bin2.setEnabled(False)
            self.chkbox_custom_bin2.setChecked(False)
            self.btn_custom_bin_browse2.setEnabled(False)
            self.label_addr2.setEnabled(False)
            self.lineEdit_addr2.setEnabled(False)
        if customer3_enable == '1':
            self.chkbox_custom_bin3.setChecked(True)
            self.lineedit_custom_bin3.setText(str(customer3_path))
            self.lineEdit_addr3.setText(str(customer3_addr))
            self.btn_custom_bin_browse3.setEnabled(True)
            self.label_addr3.setEnabled(True)
            self.lineEdit_addr3.setEnabled(True)
        else:
            self.label_custom_bin3.setEnabled(False)
            self.chkbox_custom_bin3.setChecked(False)
            self.btn_custom_bin_browse3.setEnabled(False)
            self.label_addr3.setEnabled(False)
            self.lineEdit_addr3.setEnabled(False)
        if customer4_enable == '1':
            self.chkbox_custom_bin4.setChecked(True)
            self.lineedit_custom_bin4.setText(str(customer4_path))
            self.lineEdit_addr4.setText(str(customer4_addr))
            self.btn_custom_bin_browse4.setEnabled(True)
            self.label_addr4.setEnabled(True)
            self.lineEdit_addr4.setEnabled(True)
        else:
            self.label_custom_bin4.setEnabled(False)
            self.chkbox_custom_bin4.setChecked(False)
            self.btn_custom_bin_browse4.setEnabled(False)
            self.label_addr4.setEnabled(False)
            self.lineEdit_addr4.setEnabled(False)
        self.lineedit_custom_bin1.setEnabled(False)
        self.lineedit_custom_bin2.setEnabled(False)
        self.lineedit_custom_bin3.setEnabled(False)
        self.lineedit_custom_bin4.setEnabled(False)

    def productlinecfg_dialog_load_config_from_xml(self):
        burnpath_text_1, burnpath_text_2 = xml_getxmlcfg_burnpath()
        if burnpath_text_1 != None:
            self.lineedit_bin_path_1.setText(burnpath_text_1)
        if burnpath_text_2 != None:
            self.lineedit_bin_path_2.setText(burnpath_text_2)
        cfg_list_bt_addr = xml_get_curr_bt_addr()
        btaddr_nap_text = '%02x%02x' % (cfg_list_bt_addr[0], cfg_list_bt_addr[1])
        btaddr_uap_text = '%02x' % cfg_list_bt_addr[2]
        btaddr_lap_text = '%02x%02x%02x' % (cfg_list_bt_addr[3], cfg_list_bt_addr[4], cfg_list_bt_addr[5])
        self.lineedit_btnap.setText(btaddr_nap_text)
        self.lineedit_btuap.setText(btaddr_uap_text)
        self.lineedit_btlap.setText(btaddr_lap_text)
        gen_addr_type = get_device_address_gen_type()
        self.combbx_addr_gen_type.setCurrentIndex(gen_addr_type)
        if gen_addr_type != 3:
            if xml_get_max_burn_num_enable() == 1:
                self.checkBox_burnnum.setChecked(True)
            else:
                self.checkBox_burnnum.setChecked(False)
            rest_burn_num = get_rest_burn_num()
            self.lineedit_maxburnnum.setEnabled(True)
            self.lineedit_maxburnnum.setText(str(rest_burn_num))
        cfg_localbtname = xml_get_dev_localbtname()
        buf = (c_char * 249)()
        buildinfo_bt_name_len = get_dlddll().get_build_info_bt_name(buf)
        if buildinfo_bt_name_len is not 0:
            namestr = ''
            for i in range(buildinfo_bt_name_len):
                namestr = namestr + str(buf[i])

            self.lineedit_btname.setText(namestr)
            self.lineedit_btname.setEnabled(False)
        else:
            self.lineedit_btname.setText(cfg_localbtname)
        cfg_list_ble_addr = xml_get_curr_ble_addr()
        bleaddr_nap_text = '%02x%02x' % (cfg_list_ble_addr[0], cfg_list_ble_addr[1])
        bleaddr_uap_text = '%02x' % cfg_list_ble_addr[2]
        bleaddr_lap_text = '%02x%02x%02x' % (cfg_list_ble_addr[3], cfg_list_ble_addr[4], cfg_list_ble_addr[5])
        self.lineedit_blenap.setText(bleaddr_nap_text)
        self.lineedit_bleuap.setText(bleaddr_uap_text)
        self.lineedit_blelap.setText(bleaddr_lap_text)
        cfg_localblename = xml_get_dev_localblename()
        self.lineedit_blename.setText(cfg_localblename)
        cfg_btdongle_addr = xml_get_fctrmd_btdongle_addr()
        btdongleaddr_nap_text = '%02x%02x' % (cfg_btdongle_addr[0], cfg_btdongle_addr[1])
        btdongleaddr_uap_text = '%02x' % cfg_btdongle_addr[2]
        btdongleaddr_lap_text = '%02x%02x%02x' % (cfg_btdongle_addr[3], cfg_btdongle_addr[4], cfg_btdongle_addr[5])
        self.lineedit_connectornap.setText(btdongleaddr_nap_text)
        self.lineedit_connectoruap.setText(btdongleaddr_uap_text)
        self.lineedit_connectorlap.setText(btdongleaddr_lap_text)
        cfg_calib_val = xml_getxmlcfg_default_calib_value()
        cfg_calib_text = str('%d' % cfg_calib_val)
        self.lineedit_default_calibval.setText(cfg_calib_text)
        gen_sn_type = xml_get_sn_gen_type()
        self.combbx_sn_gen_type.setCurrentIndex(int(gen_sn_type))
        sn = xml_get_curr_sn()
        self.lineedit_sn.setText(sn)
        if xml_get_update_btaddr_enable() == 1:
            self.checkBox_btaddr.setChecked(True)
        else:
            self.checkBox_btaddr.setChecked(False)
        if xml_get_update_btname_enable() == 1:
            self.checkBox_btname.setChecked(True)
        else:
            self.checkBox_btname.setChecked(False)
        if xml_get_update_bleaddr_enable() == 1:
            self.checkBox_bleaddr.setChecked(True)
        else:
            self.checkBox_bleaddr.setChecked(False)
        if xml_get_update_blename_enable() == 1:
            self.checkBox_blename.setChecked(True)
        else:
            self.checkBox_blename.setChecked(False)
        if xml_get_update_conaddr_enable() == 1:
            self.checkBox_conaddr.setChecked(True)
        else:
            self.checkBox_conaddr.setChecked(False)
        if xml_get_update_calib_enable() == 1:
            self.checkBox_calib.setChecked(True)
        else:
            self.checkBox_calib.setChecked(False)
        if xml_get_update_sector_enable() == '1':
            self.checkbox_update_sector.setChecked(True)
        else:
            self.checkbox_update_sector.setChecked(False)
        if xml_get_update_sn_enable() == 1:
            self.checkBox_sn.setChecked(True)
        else:
            self.checkBox_sn.setChecked(False)
        if cfg_as_updatetool() is False:
            if xml_get_connector_cfg() == '1':
                self.factorymode_connect_switch.setChecked(True)
            else:
                self.factorymode_connect_switch.setChecked(False)
            if xml_get_calibrate_cfg() == '1':
                self.factorymode_calib_switch.setChecked(True)
            else:
                self.factorymode_calib_switch.setChecked(False)
        if xml_get_app_switch() == '1':
            self.chkbox_app.setChecked(True)
            self.label_app.setEnabled(True)
            self.lineedit_bin_path_1.setEnabled(True)
            self.push_btn_browse_1.setEnabled(True)
            self.chkbox_appcrc.setEnabled(True)
        else:
            self.chkbox_app.setChecked(False)
            self.label_app.setEnabled(False)
            self.lineedit_bin_path_1.setEnabled(False)
            self.push_btn_browse_1.setEnabled(False)
            self.chkbox_appcrc.setEnabled(False)
            self.chkbox_appcrc.setChecked(False)
            self.label_bin_verify.setEnabled(False)
            self.lineedit_hash_1.setEnabled(False)
        if xml_get_otaboot_switch() == '1':
            self.chkbox_boot.setChecked(True)
            self.label_boot.setEnabled(True)
            self.lineedit_bin_path_2.setEnabled(True)
            self.push_btn_browse_2.setEnabled(True)
            self.chkbox_bootcrc.setEnabled(True)
        else:
            self.chkbox_boot.setChecked(False)
            self.label_boot.setEnabled(False)
            self.lineedit_bin_path_2.setEnabled(False)
            self.push_btn_browse_2.setEnabled(False)
            self.chkbox_bootcrc.setEnabled(False)
            self.chkbox_bootcrc.setChecked(False)
            self.label_bin_verify_2.setEnabled(False)
            self.lineedit_hash_2.setEnabled(False)
        if xml_get_btfname_switch() == '1':
            self.chkbox_filename.setChecked(True)
        else:
            self.chkbox_filename.setChecked(False)
        if xml_get_erasewhole_switch() == '1':
            self.checkbox_erase_whole.setChecked(True)
        else:
            self.checkbox_erase_whole.setChecked(False)
        verify_hash_text_1, verify_hash_text_2 = xml_get_verify_text()
        if xml_get_verifycrc1_switch() == '1':
            self.chkbox_appcrc.setChecked(True)
            self.label_bin_verify.setEnabled(True)
            self.lineedit_hash_1.setEnabled(True)
            if verify_hash_text_1 != None:
                self.lineedit_hash_1.setText(verify_hash_text_1)
        else:
            self.chkbox_appcrc.setChecked(False)
            self.label_bin_verify.setEnabled(False)
            self.lineedit_hash_1.setEnabled(False)
        if xml_get_verifycrc2_switch() == '1':
            self.chkbox_bootcrc.setChecked(True)
            self.label_bin_verify_2.setEnabled(True)
            self.lineedit_hash_2.setEnabled(True)
            if verify_hash_text_2 != None:
                self.lineedit_hash_2.setText(verify_hash_text_2)
        else:
            self.chkbox_bootcrc.setChecked(False)
            self.label_bin_verify_2.setEnabled(False)
            self.lineedit_hash_2.setEnabled(False)
        self.custom_bin_widget_gui_init()
        return

    def init_productline_config_dialog(self):
        self.productlinecfg_dialog_load_config_from_xml()
        if xml_getxmlcfg_is_onlyburn() == True or xml_getxmlcfg_is_burnandfctrmd() == True:
            self.checkbox_burn_switch.setChecked(True)
            self.burn_group_setting_setenabled(True)
        else:
            self.checkbox_burn_switch.setChecked(False)
            self.burn_group_setting_setenabled(False)
        if cfg_as_updatetool() is False:
            if xml_get_factorymode_cfg() == '1':
                self.checkbox_factory_switch.setChecked(True)
                self.factorymode_group_setting_setenabled(True)
            else:
                self.checkbox_factory_switch.setChecked(False)
                self.factorymode_group_setting_setenabled(False)

    def convert_addr_lap_to_hex_str(self, lap_text):
        lap_hex_str = '0x' + lap_text[0:2] + ',' + '0x' + lap_text[2:4] + ',' + '0x' + lap_text[4:6]
        return str(lap_hex_str)

    def convert_addr_uap_to_hex_str(self, uap_text):
        uap_hex_str = '0x' + uap_text[0:2]
        return str(uap_hex_str)

    def convert_addr_nap_to_hex_str(self, nap_text):
        nap_hex_str = '0x' + nap_text[0:2] + ',' + '0x' + nap_text[2:4]
        return str(nap_hex_str)

    def factoryline_configure_save_slot(self):
        custom_bin1_addr = self.lineEdit_addr1.text()
        custom_bin2_addr = self.lineEdit_addr2.text()
        custom_bin3_addr = self.lineEdit_addr3.text()
        custom_bin4_addr = self.lineEdit_addr4.text()
        if self.custom_bin1_path != '' and custom_bin1_addr == '' or self.custom_bin2_path != '' and custom_bin2_addr == '' or self.custom_bin3_path != '' and custom_bin3_addr == '' or self.custom_bin4_path != '' and custom_bin4_addr == '':
            error_dlg = ErrorReportDlg('The bin file flash addr is null!')
            error_dlg.exec_()
            return
        else:
            if not self.chkbox_app.isChecked() and not self.chkbox_boot.isChecked():
                get_dlddll().set_chiptype_value(str(self.comboBox_chipver.currentText()))
            encrypt_on = xml_encrypt_is_on()
            if encrypt_on is True:
                file_path = self.lineedit_bin_path_1.text().replace('/', '\\\\')
                bin_judge_ret = get_dlddll().judge_bin_file_is_valid(str(file_path))
                if bin_judge_ret == 2:
                    error_dlg = ErrorReportDlg('The current bin file is not encrypt mode!')
                    error_dlg.exec_()
                    return
            self.saveed_data_list = []
            checkbox_burn_checked = self.checkbox_burn_switch.isChecked()
            if checkbox_burn_checked == True:
                save_burned_switch = '1'
            else:
                save_burned_switch = '0'
            save_bin_path_text_1 = str(self.lineedit_bin_path_1.text())
            save_verinfo_text_1 = str(self.lineedit_hash_1.text())
            verify_appcrc_checked = self.chkbox_appcrc.isChecked()
            if verify_appcrc_checked == True:
                save_appcrc_switch = '1'
            else:
                save_appcrc_switch = '0'
            verify_bootcrc_checked = self.chkbox_bootcrc.isChecked()
            if verify_bootcrc_checked == True:
                save_bootcrc_switch = '1'
            else:
                save_bootcrc_switch = '0'
            app_checked = self.chkbox_app.isChecked()
            if app_checked == True:
                save_app_switch = '1'
            else:
                save_app_switch = '0'
            boot_checked = self.chkbox_boot.isChecked()
            if boot_checked == True:
                save_boot_switch = '1'
            else:
                save_boot_switch = '0'
            if app_checked and save_bin_path_text_1 == '':
                error_dlg = ErrorReportDlg('请选择APP文件!')
                error_dlg.exec_()
                return
            if save_verinfo_text_1 == '' and verify_appcrc_checked:
                error_dlg = ErrorReportDlg('请配置APP文件CRC!')
                error_dlg.exec_()
                return
            save_bin_path_text_2 = str(self.lineedit_bin_path_2.text())
            save_verinfo_text_2 = str(self.lineedit_hash_2.text())
            if boot_checked and save_bin_path_text_2 == '':
                error_dlg = ErrorReportDlg('请选择OTA BOOT文件!')
                error_dlg.exec_()
                return
            if boot_checked:
                if app_checked is False:
                    error_dlg = ErrorReportDlg('you must choose app box!')
                    error_dlg.exec_()
                    return
            if save_verinfo_text_2 == '' and verify_bootcrc_checked:
                error_dlg = ErrorReportDlg('请配置OTA BOOT文件CRC!')
                error_dlg.exec_()
                return
            btfname_checked = self.chkbox_filename.isChecked()
            if btfname_checked == True:
                save_btfname_switch = '1'
            else:
                save_btfname_switch = '0'
            erasewhole_checked = self.checkbox_erase_whole.isChecked()
            if erasewhole_checked == True:
                save_erasewhole_switch = '1'
            else:
                save_erasewhole_switch = '0'
            checkbox_update_sector_checked = self.checkbox_update_sector.isChecked()
            if checkbox_update_sector_checked == True:
                save_update_sector_switch = '1'
            else:
                save_update_sector_switch = '0'
            save_addr_gen_type_text = str(self.combbx_addr_gen_type.currentIndex())
            save_sn_gen_type_text = str(self.combbx_sn_gen_type.currentIndex())
            bt_addr_lap_text = self.lineedit_btlap.text()
            save_bt_addr_lap_text = self.convert_addr_lap_to_hex_str(bt_addr_lap_text)
            bt_addr_uap_text = self.lineedit_btuap.text()
            save_bt_addr_uap_text = self.convert_addr_uap_to_hex_str(bt_addr_uap_text)
            bt_addr_nap_text = self.lineedit_btnap.text()
            save_bt_addr_nap_text = self.convert_addr_nap_to_hex_str(bt_addr_nap_text)
            if len(bt_addr_lap_text) != 6 or len(bt_addr_uap_text) != 2 or len(bt_addr_nap_text) != 4:
                error_dlg = ErrorReportDlg('Bt Address配置错误')
                error_dlg.exec_()
                return
            save_bt_localname_text = str(self.lineedit_btname.text()).rstrip()
            ble_addr_lap_text = self.lineedit_blelap.text()
            save_ble_addr_lap_text = self.convert_addr_lap_to_hex_str(ble_addr_lap_text)
            ble_addr_uap_text = self.lineedit_bleuap.text()
            save_ble_addr_uap_text = self.convert_addr_uap_to_hex_str(ble_addr_uap_text)
            ble_addr_nap_text = self.lineedit_blenap.text()
            save_ble_addr_nap_text = self.convert_addr_nap_to_hex_str(ble_addr_nap_text)
            save_ble_localname_text = str(self.lineedit_blename.text()).rstrip()
            save_sn_text = str(self.lineedit_sn.text()).rstrip()
            connector_addr_lap_text = self.lineedit_connectorlap.text()
            save_connector_addr_lap_text = self.convert_addr_lap_to_hex_str(connector_addr_lap_text)
            connector_addr_uap_text = self.lineedit_connectoruap.text()
            save_connector_addr_uap_text = self.convert_addr_uap_to_hex_str(connector_addr_uap_text)
            connector_addr_nap_text = self.lineedit_connectornap.text()
            save_connector_addr_nap_text = self.convert_addr_nap_to_hex_str(connector_addr_nap_text)
            update_btaddr = self.checkBox_btaddr.isChecked()
            if update_btaddr:
                save_update_btaddr_switch = '1'
            else:
                save_update_btaddr_switch = '0'
            update_btname = self.checkBox_btname.isChecked()
            if update_btname:
                save_update_btname_switch = '1'
            else:
                save_update_btname_switch = '0'
            update_bleaddr = self.checkBox_bleaddr.isChecked()
            if update_bleaddr:
                save_update_bleaddr_switch = '1'
            else:
                save_update_bleaddr_switch = '0'
            update_blename = self.checkBox_blename.isChecked()
            if update_blename:
                save_update_blename_switch = '1'
            else:
                save_update_blename_switch = '0'
            update_conaddr = self.checkBox_conaddr.isChecked()
            if update_conaddr:
                save_update_conaddr_switch = '1'
            else:
                save_update_conaddr_switch = '0'
            update_calibbox = self.checkBox_calib.isChecked()
            if update_calibbox:
                save_update_calibbox_switch = '1'
            else:
                save_update_calibbox_switch = '0'
            update_sn = self.checkBox_sn.isChecked()
            if update_sn:
                save_update_sn_switch = '1'
            else:
                save_update_sn_switch = '0'
            save_calib_text = str(self.lineedit_default_calibval.text())
            if cfg_as_updatetool() is False:
                checkbox_factorymode_checked = self.checkbox_factory_switch.isChecked()
                if checkbox_factorymode_checked:
                    save_factorymode_switch = '1'
                else:
                    save_factorymode_switch = '0'
                checkbox_calib_checked = self.factorymode_calib_switch.isChecked()
                if checkbox_calib_checked:
                    save_calib_switch = '1'
                else:
                    save_calib_switch = '0'
                checkbox_connector_checked = self.factorymode_connect_switch.isChecked()
                if checkbox_connector_checked:
                    save_connector_switch = '1'
                else:
                    save_connector_switch = '0'
                if save_calib_switch == '0' and save_connector_switch == '0':
                    save_factorymode_switch = '0'
                if save_factorymode_switch == '0' and save_burned_switch == '0':
                    error_dlg = ErrorReportDlg('burn or factorymode switch cfg error.')
                    error_dlg.exec_()
                    return
            save_chipver = str(self.comboBox_chipver.currentText())
            if self.chkbox_custom_bin1.isChecked():
                save_custom_bin1_switch = '1'
                save_custom_bin1_path = str(self.lineedit_custom_bin1.text())
                save_custom_bin1_addr = str(self.lineEdit_addr1.text())
            else:
                save_custom_bin1_switch = '0'
                save_custom_bin1_path = ''
                save_custom_bin1_addr = ''
            if self.chkbox_custom_bin2.isChecked():
                save_custom_bin2_switch = '1'
                save_custom_bin2_path = str(self.lineedit_custom_bin2.text())
                save_custom_bin2_addr = str(self.lineEdit_addr2.text())
            else:
                save_custom_bin2_switch = '0'
                save_custom_bin2_path = ''
                save_custom_bin2_addr = ''
            if self.chkbox_custom_bin3.isChecked():
                save_custom_bin3_switch = '1'
                save_custom_bin3_path = str(self.lineedit_custom_bin3.text())
                save_custom_bin3_addr = str(self.lineEdit_addr3.text())
            else:
                save_custom_bin3_switch = '0'
                save_custom_bin3_path = ''
                save_custom_bin3_addr = ''
            if self.chkbox_custom_bin4.isChecked():
                save_custom_bin4_switch = '1'
                save_custom_bin4_path = str(self.lineedit_custom_bin4.text())
                save_custom_bin4_addr = str(self.lineEdit_addr4.text())
            else:
                save_custom_bin4_switch = '0'
                save_custom_bin4_path = ''
                save_custom_bin4_addr = ''
            if self.chkbox_erase_en.isChecked():
                erase_en = True
                erase_len = str(self.lineEdit_eraselen.text())
                erase_addr = str(self.lineEdit_erase_addr.text())
            else:
                erase_en = False
                erase_len = 0
                erase_addr = None
            set_erase_info(erase_en, erase_len, erase_addr)
            checkbox_burnnum_checked = self.checkBox_burnnum.isChecked()
            if checkbox_burnnum_checked:
                save_burnnum_switch = '1'
            else:
                save_burnnum_switch = '0'
            if checkbox_burnnum_checked:
                if get_max_burn_num_flag() and \
                        (self.lineedit_maxburnnum.text() == '' or self.lineedit_maxburnnum.text() == '0'):
                    error_dlg = ErrorReportDlg('max burn number is error.')
                    error_dlg.exec_()
                    return
                save_max_burn_num = str(self.lineedit_maxburnnum.text())
            else:
                save_max_burn_num = '0'
            self.saveed_data_list.append(save_burned_switch)
            self.saveed_data_list.append(save_bin_path_text_1)
            self.saveed_data_list.append(save_verinfo_text_1)
            self.saveed_data_list.append(save_bin_path_text_2)
            self.saveed_data_list.append(save_verinfo_text_2)
            self.saveed_data_list.append(save_update_sector_switch)
            self.saveed_data_list.append(save_addr_gen_type_text)
            self.saveed_data_list.append(save_bt_addr_lap_text)
            self.saveed_data_list.append(save_bt_addr_uap_text)
            self.saveed_data_list.append(save_bt_addr_nap_text)
            self.saveed_data_list.append(save_bt_localname_text)
            self.saveed_data_list.append(save_ble_addr_lap_text)
            self.saveed_data_list.append(save_ble_addr_uap_text)
            self.saveed_data_list.append(save_ble_addr_nap_text)
            self.saveed_data_list.append(save_ble_localname_text)
            self.saveed_data_list.append(save_connector_addr_lap_text)
            self.saveed_data_list.append(save_connector_addr_uap_text)
            self.saveed_data_list.append(save_connector_addr_nap_text)
            self.saveed_data_list.append(save_update_btaddr_switch)
            self.saveed_data_list.append(save_update_btname_switch)
            self.saveed_data_list.append(save_update_bleaddr_switch)
            self.saveed_data_list.append(save_update_blename_switch)
            self.saveed_data_list.append(save_update_conaddr_switch)
            self.saveed_data_list.append(save_update_calibbox_switch)
            self.saveed_data_list.append(save_calib_text)
            self.saveed_data_list.append(save_appcrc_switch)
            self.saveed_data_list.append(save_bootcrc_switch)
            self.saveed_data_list.append(save_app_switch)
            self.saveed_data_list.append(save_boot_switch)
            self.saveed_data_list.append(save_btfname_switch)
            self.saveed_data_list.append(save_chipver)
            self.saveed_data_list.append(save_custom_bin1_switch)
            self.saveed_data_list.append(save_custom_bin1_path)
            self.saveed_data_list.append(save_custom_bin1_addr)
            self.saveed_data_list.append(save_custom_bin2_switch)
            self.saveed_data_list.append(save_custom_bin2_path)
            self.saveed_data_list.append(save_custom_bin2_addr)
            self.saveed_data_list.append(save_custom_bin3_switch)
            self.saveed_data_list.append(save_custom_bin3_path)
            self.saveed_data_list.append(save_custom_bin3_addr)
            self.saveed_data_list.append(save_custom_bin4_switch)
            self.saveed_data_list.append(save_custom_bin4_path)
            self.saveed_data_list.append(save_custom_bin4_addr)
            self.saveed_data_list.append(save_sn_gen_type_text)
            self.saveed_data_list.append(save_sn_text)
            self.saveed_data_list.append(save_update_sn_switch)
            self.saveed_data_list.append(save_erasewhole_switch)
            self.saveed_data_list.append(save_burnnum_switch)
            self.saveed_data_list.append(save_max_burn_num)
            if cfg_as_updatetool() is False:
                self.saveed_data_list.append(save_factorymode_switch)
                self.saveed_data_list.append(save_calib_switch)
                self.saveed_data_list.append(save_connector_switch)
            xml_save_productlinecfg_dlg_data(self.saveed_data_list)
            self.accept()
            return

    def factory_switch_slot(self):
        checkbox_status = self.checkbox_factory_switch.isChecked()
        self.groupBox_factorymode_setting.setEnabled(checkbox_status)

    def burn_switch_slot(self):
        if self.checkbox_burn_switch.isChecked() == True:
            self.burn_switch = True
            self.burn_group_setting_setenabled(True)
        else:
            self.burn_switch = False
            self.burn_group_setting_setenabled(False)

    def update_sector_slot(self):
        ischecked = self.checkbox_update_sector.isChecked()
        if ischecked is True or ischecked is False:
            self.groupBox.setEnabled(ischecked)
        else:
            AssertionError

    def factorymode_group_setting_setenabled(self, factorymode_on):
        if factorymode_on == True or factorymode_on == False:
            self.groupBox_factorymode_setting.setEnabled(factorymode_on)
        else:
            AssertionError

    def burn_group_setting_setenabled(self, burn_on):
        if burn_on:
            self.groupBox_burn_setting.setEnabled(True)
            if self.checkbox_update_sector.isChecked() == False:
                self.groupBox.setEnabled(False)
        elif not burn_on:
            self.groupBox_burn_setting.setEnabled(False)
        else:
            AssertionError

    def showappbrowse(self):
        strlist = []
        if self.chkbox_app.isChecked():
            self.label_app.setEnabled(True)
            self.lineedit_bin_path_1.setEnabled(True)
            self.push_btn_browse_1.setEnabled(True)
            self.chkbox_appcrc.setEnabled(True)
            if self.chkbox_filename.isChecked() and self.checkbox_update_sector.isChecked():
                if self.lineedit_bin_path_1.text() != '':
                    strlist = self.lineedit_bin_path_1.text().split('/')
                    strlen = len(strlist)
                    filename = strlist[strlen - 1].split('.')[0]
                    self.lineedit_btname.setText(filename)
        else:
            self.label_app.setEnabled(False)
            self.lineedit_bin_path_1.setEnabled(False)
            self.push_btn_browse_1.setEnabled(False)
            self.chkbox_appcrc.setEnabled(False)
            self.chkbox_appcrc.setChecked(False)
            self.label_bin_verify.setEnabled(False)
            self.lineedit_hash_1.setEnabled(False)
            self.lineedit_bin_path_1.setText('')
            self.lineedit_hash_1.setText('')
            if self.chkbox_boot.isChecked() and self.chkbox_filename.isChecked() and self.checkbox_update_sector.isChecked():
                if self.lineedit_bin_path_2.text() != '':
                    strlist = self.lineedit_bin_path_2.text().split('/')
                    strlen = len(strlist)
                    filename = strlist[strlen - 1].split('.')[0]
                    self.lineedit_btname.setText(filename)

    def showbootbrowse(self):
        strlist = []
        if self.chkbox_boot.isChecked():
            self.label_boot.setEnabled(True)
            self.lineedit_bin_path_2.setEnabled(True)
            self.push_btn_browse_2.setEnabled(True)
            self.chkbox_bootcrc.setEnabled(True)
            if not self.chkbox_app.isChecked() and self.chkbox_filename.isChecked() and self.checkbox_update_sector.isChecked():
                if self.lineedit_bin_path_2.text() != '':
                    strlist = self.lineedit_bin_path_2.text().split('/')
                    strlen = len(strlist)
                    filename = strlist[strlen - 1].split('.')[0]
                    self.lineedit_btname.setText(filename)
        else:
            self.label_boot.setEnabled(False)
            self.lineedit_bin_path_2.setEnabled(False)
            self.push_btn_browse_2.setEnabled(False)
            self.chkbox_bootcrc.setEnabled(False)
            self.chkbox_bootcrc.setChecked(False)
            self.label_bin_verify_2.setEnabled(False)
            self.lineedit_hash_2.setEnabled(False)
            self.lineedit_bin_path_2.setText('')
            self.lineedit_hash_2.setText('')

    def setbtname(self):
        strlist = []
        if self.chkbox_filename.isChecked() and self.checkbox_update_sector.isChecked():
            if self.chkbox_app.isChecked() and self.lineedit_bin_path_1.text() != '':
                strlist = self.lineedit_bin_path_1.text().split('/')
                strlen = len(strlist)
                filename = strlist[strlen - 1].split('.')[0]
            elif not self.chkbox_app.isChecked() and self.chkbox_boot.isChecked() and self.lineedit_bin_path_2.text() != '':
                strlist = self.lineedit_bin_path_2.text().split('/')
                strlen = len(strlist)
                filename = strlist[strlen - 1].split('.')[0]
            else:
                error_dlg = ErrorReportDlg('请选择文件!')
                error_dlg.exec_()
                self.chkbox_filename.setChecked(False)
                return
            self.label_5.setEnabled(False)
            self.lineedit_btname.setEnabled(False)
            self.lineedit_btname.setText(filename)
        elif not self.chkbox_filename.isChecked() and self.checkbox_update_sector.isChecked():
            self.label_5.setEnabled(True)
            self.lineedit_btname.setEnabled(True)

    def showappcrc(self):
        if self.chkbox_appcrc.isChecked():
            self.label_bin_verify.setEnabled(True)
            self.lineedit_hash_1.setEnabled(True)
        else:
            self.label_bin_verify.setEnabled(False)
            self.lineedit_hash_1.setEnabled(False)

    def showbootcrc(self):
        if self.chkbox_bootcrc.isChecked():
            self.label_bin_verify_2.setEnabled(True)
            self.lineedit_hash_2.setEnabled(True)
        else:
            self.label_bin_verify_2.setEnabled(False)
            self.lineedit_hash_2.setEnabled(False)

    def en_disn_able_custom_bin1_widgets(self):
        """enable or disable custom bin1 widgets"""
        if self.chkbox_custom_bin1.isChecked():
            self.label_custom_bin1.setEnabled(True)
            self.btn_custom_bin_browse1.setEnabled(True)
            self.label_addr1.setEnabled(True)
            self.lineEdit_addr1.setEnabled(True)
        else:
            self.label_custom_bin1.setEnabled(False)
            self.label_addr1.setEnabled(False)
            self.lineEdit_addr1.setEnabled(False)
            self.btn_custom_bin_browse1.setEnabled(False)

    def en_disn_able_custom_bin2_widgets(self):
        """enable or disable custom bin2 widgets"""
        if self.chkbox_custom_bin2.isChecked():
            self.label_custom_bin2.setEnabled(True)
            self.btn_custom_bin_browse2.setEnabled(True)
            self.label_addr2.setEnabled(True)
            self.lineEdit_addr2.setEnabled(True)
        else:
            self.label_custom_bin2.setEnabled(False)
            self.label_addr2.setEnabled(False)
            self.lineEdit_addr2.setEnabled(False)
            self.btn_custom_bin_browse2.setEnabled(False)

    def en_disn_able_custom_bin3_widgets(self):
        """enable or disable custom bin1 widgets"""
        if self.chkbox_custom_bin3.isChecked():
            self.label_custom_bin3.setEnabled(True)
            self.btn_custom_bin_browse3.setEnabled(True)
            self.label_addr3.setEnabled(True)
            self.lineEdit_addr3.setEnabled(True)
        else:
            self.label_custom_bin3.setEnabled(False)
            self.label_addr3.setEnabled(False)
            self.lineEdit_addr3.setEnabled(False)
            self.btn_custom_bin_browse3.setEnabled(False)

    def en_disn_able_custom_bin4_widgets(self):
        """enable or disable custom bin4 widgets"""
        if self.chkbox_custom_bin4.isChecked():
            self.label_custom_bin4.setEnabled(True)
            self.btn_custom_bin_browse4.setEnabled(True)
            self.label_addr4.setEnabled(True)
            self.lineEdit_addr4.setEnabled(True)
        else:
            self.label_custom_bin4.setEnabled(False)
            self.label_addr4.setEnabled(False)
            self.lineEdit_addr4.setEnabled(False)
            self.btn_custom_bin_browse4.setEnabled(False)
