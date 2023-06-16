#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2023-02-17 14:28:54
# @File: dld_xml_operate.py
# @Author: YeHwong
# @Email: 598316810@qq.com
# @Version ：1.0.0
import copy
import struct
import os
import xml.etree.ElementTree as Et
from dld_global import save_log_to_file, get_dlddll, get_mainproc_monitor_mutex, \
    c_char, bes_trace, set_g_efuseID1, set_g_efuseID2

g_burn_path_1 = ''
g_burn_path_2 = ''
g_verify_text_1 = ''
g_verify_text_2 = ''
default_calib_value = 0
default_calib_value2 = 0
root_parse = ''
g_max_num_enable = '0'
g_update_sector_enable = '0'
g_update_btaddr_enable = '0'
g_update_btname_enable = '0'
g_update_bleaddr_enable = '0'
g_update_blename_enable = '0'
g_update_conaddr_enable = '0'
g_update_calib_enable = '0'
g_customer1_enable = '0'
g_customer1_path = ''
g_customer1_addr = ''
g_customer2_enable = '0'
g_customer2_path = ''
g_customer2_addr = ''
g_customer3_enable = '0'
g_customer3_path = ''
g_customer3_addr = ''
g_customer4_enable = '0'
g_customer4_path = ''
g_customer4_addr = ''
g_chip_version = '1000'
g_erase_enable = False
g_erase_len = 0
g_erase_addr = []
g_sn_gen_type = 0
g_update_sn_enable = '0'
g_sn = []
g_update_sn_root = ''
g_update_Customized_enable = []
g_update_Customized_Addr = '0'
g_setmax_root = ''
g_dev_addr_gen_type = 1
updatebtaddr = ''
curr_bt_addr_gen = []
currbtaddr_root = ''
auto_gen_ble_addr_flag = 0
curr_ble_addr_gen = []
currbleaddr_root = ''
g_gen_ble_addr = [0, 0, 0, 0, 0, 0]
g_dev_localbtname = []
g_dev_localblename = []
g_fctrmd_bt_dongle_addr = []
g_factorymode_switch = '0'
g_fctrmd_calib_switch = '0'
g_fctrmd_connector_switch = '0'
g_onlyburn_switch = False
g_onlyfactorymode_switch = False
g_burnandfactorymode_switch = False
g_dldresult_root = ''
g_dld_complete_count = 0
g_dld_failure_count = 0
g_language_cfg = ""
g_cfgasupdate_flag = '0'
g_verifycrc1_switch = '0'
g_verifycrc2_switch = '0'
g_app_switch = '0'
g_otaboot_switch = '0'
g_btfname_switch = '0'
g_erasewhole_switch = '0'
g_encrypt_on = False
g_failed_btaddr = []
g_failed_bleaddr = []
g_using_btaddr = []
g_using_bleaddr = []
g_burnappota_only = '1'
g_baudrate = '921600'
g_rest_burn_num = 0
g_delay_time = 0

def get_device_address_gen_type():
    global g_dev_addr_gen_type
    return g_dev_addr_gen_type


def set_device_address_gen_type(gen_type):
    global g_dev_addr_gen_type
    assert gen_type == 0 or gen_type == 1 or gen_type == 2 or gen_type == 3, 'gen_type must be the following ' \
                                                                             'option:0|1|2|3 '
    g_dev_addr_gen_type = gen_type


def get_rest_burn_num():
    global g_rest_burn_num
    return g_rest_burn_num


def set_rest_burn_num(num):
    global g_rest_burn_num
    g_rest_burn_num = num


def xml_get_sn_gen_type():
    global g_sn_gen_type
    return g_sn_gen_type


def xml_get_delay_time():
    global g_delay_time
    return g_delay_time


def xml_get_update_Customized_enable():
    global g_update_Customized_enable
    if g_update_Customized_enable == '1':
        return 1
    return 0


def xml_get_update_Customized_Addr():
    global g_update_Customized_Addr
    return g_update_Customized_Addr


def set_sn_gen_type(gen_type):
    global g_sn_gen_type
    assert gen_type == 0 or gen_type == 1, 'gen_type must be the following option:0|1'
    g_sn_gen_type = gen_type


def xml_get_update_sn_enable():
    global g_update_sn_enable
    if g_update_sn_enable == '1':
        return 1
    return 0


def xml_getxmlcfg_burnpath():
    global g_burn_path_1
    global g_burn_path_2
    return (
        g_burn_path_1, g_burn_path_2)


def xml_get_verify_text():
    global g_verify_text_1
    global g_verify_text_2
    return (
        g_verify_text_1, g_verify_text_2)


def xml_getxmlcfg_default_calib_value():
    global default_calib_value
    global default_calib_value2
    chiptypestr = ''
    buf = (c_char * 20)()
    chiptype_len = get_dlddll().get_chiptype_value(buf)
    if chiptype_len is not 0:
        for i in range(chiptype_len):
            chiptypestr = chiptypestr + str(buf[i])

    if chiptypestr == '1400' or chiptypestr == '1501':
        return default_calib_value2
    return default_calib_value


def xml_getxmlcfg_is_fctrmdonly():
    global g_onlyfactorymode_switch
    return g_onlyfactorymode_switch


def xml_getxmlcfg_is_onlyburn():
    global g_onlyburn_switch
    return g_onlyburn_switch


def xml_getxmlcfg_is_burnandfctrmd():
    global g_burnandfactorymode_switch
    return g_burnandfactorymode_switch


def xmL_get_doc():
    global doc_parse
    return doc_parse


def xmL_get_root():
    global root_parse
    return root_parse


def xml_get_curr_bt_addr():
    global curr_bt_addr_gen
    return curr_bt_addr_gen


def get_btaddr_lap_uint(list_btaddr):
    uint_lap = list_btaddr[3] | list_btaddr[4] << 8 | list_btaddr[5] << 16
    return uint_lap


def xml_set_curr_sn(sn):
    global g_sn
    g_sn = copy.deepcopy(sn)


def xml_get_curr_sn():
    return g_sn


def xml_get_curr_ble_addr():
    global curr_ble_addr_gen
    return curr_ble_addr_gen


def xml_set_curraddr(btaddr):
    global curr_bt_addr_gen
    curr_bt_addr_gen = copy.deepcopy(btaddr)


def xml_update_ble_addr(bleaddr):
    global curr_ble_addr_gen
    curr_ble_addr_gen = copy.deepcopy(bleaddr)


def xml_get_failed_bt_addr():
    global g_failed_btaddr
    return g_failed_btaddr


def xml_get_failed_ble_addr():
    global g_failed_bleaddr
    return g_failed_bleaddr


def xml_set_failed_bt_addr(btaddr):
    global g_failed_btaddr
    g_failed_btaddr = copy.deepcopy(btaddr)


def xml_set_failed_ble_addr(bleaddr):
    global g_failed_bleaddr
    g_failed_bleaddr = copy.deepcopy(bleaddr)


def get_using_bt_addr():
    global g_using_btaddr
    return g_using_btaddr


def get_using_ble_addr():
    global g_using_bleaddr
    return g_using_bleaddr


def set_using_bt_addr(btaddr):
    global g_using_btaddr
    g_using_btaddr = copy.deepcopy(btaddr)


def set_using_ble_addr(bleaddr):
    global g_using_bleaddr
    g_using_bleaddr = copy.deepcopy(bleaddr)


def cfg_as_updatetool():
    global g_cfgasupdate_flag
    if g_cfgasupdate_flag == '1':
        return True
    return False


def burn_appota_only():
    global g_burnappota_only
    if g_burnappota_only == '1':
        return True
    return False


def get_baudrate():
    global g_baudrate
    return g_baudrate


def get_xmlcfg_language():
    global g_language_cfg
    if g_language_cfg == "":
        xml_doc_parse()
    lang_low_str = g_language_cfg.lower()
    if lang_low_str != 'cn' and lang_low_str != 'en':
        return 'error'
    else:
        return g_language_cfg


def xml_get_verifycrc1_switch():
    global g_verifycrc1_switch
    return g_verifycrc1_switch


def xml_get_verifycrc2_switch():
    global g_verifycrc2_switch
    return g_verifycrc2_switch


def xml_get_app_switch():
    global g_app_switch
    return g_app_switch


def xml_get_otaboot_switch():
    global g_otaboot_switch
    return g_otaboot_switch


def xml_get_btfname_switch():
    global g_btfname_switch
    return g_btfname_switch


def xml_get_erasewhole_switch():
    global g_erasewhole_switch
    return g_erasewhole_switch


def xml_save_productlinecfg_dlg_data(cfg_data):
    global g_failed_bleaddr
    global g_failed_btaddr
    global g_using_bleaddr
    global g_using_btaddr
    root_parse = doc_parse.getroot()
    burn_root_item = root_parse.find('burn')
    burn_root_item.set('switch', cfg_data[0])
    burn_root_item.find('burnpath_1').text = cfg_data[1]
    burn_root_item.find('verify_hash_1').text = cfg_data[2]
    burn_root_item.find('burnpath_2').text = cfg_data[3]
    burn_root_item.find('verify_hash_2').text = cfg_data[4]
    updatesector_root_item = burn_root_item.find('updatesector')
    updatesector_root_item.set('enable', cfg_data[5])
    updatesector_root_item.find('addr_gen_type').text = cfg_data[6]
    updatebtaddr_root = updatesector_root_item.find('updatebtaddr')
    updatebtaddr_root.set('enable', cfg_data[18])
    updatebtaddr_root_item = updatebtaddr_root.find('curr_bt_addr_gen')
    BtLapStr = updatebtaddr_root_item.find('LAP').text
    BtUapStr = updatebtaddr_root_item.find('UAP').text
    BtNapStr = updatebtaddr_root_item.find('NAP').text
    origiBtAddrStr = BtLapStr + ',' + BtUapStr + ',' + BtNapStr
    updatabtAddrStr = cfg_data[7] + ',' + cfg_data[8] + ',' + cfg_data[9]
    if origiBtAddrStr != updatabtAddrStr:
        root_parse.find('unuse_bt_addr').text = ''
        root_parse.find('unuse_ble_addr').text = ''
        g_failed_btaddr = []
        g_failed_bleaddr = []
        g_using_btaddr = []
        g_using_bleaddr = []
    updatebtaddr_root_item.find('LAP').text = cfg_data[7]
    updatebtaddr_root_item.find('UAP').text = cfg_data[8]
    updatebtaddr_root_item.find('NAP').text = cfg_data[9]
    updatebtname_root = updatesector_root_item.find('updatebtname')
    updatebtname_root.set('enable', cfg_data[19])
    updatebtname_root.find('dev_localname').text = cfg_data[10]
    updatebleaddr_root = updatesector_root_item.find('updatebleaddr')
    updatebleaddr_root.set('enable', cfg_data[20])
    updatebleaddr_root_item = updatebleaddr_root.find('curr_ble_addr_gen')
    updatebleaddr_root_item.find('LAP').text = cfg_data[11]
    updatebleaddr_root_item.find('UAP').text = cfg_data[12]
    updatebleaddr_root_item.find('NAP').text = cfg_data[13]
    updateblename_root = updatesector_root_item.find('updateblename')
    updateblename_root.set('enable', cfg_data[21])
    updateblename_root.find('dev_localname').text = cfg_data[14]
    btdongleaddr_root = updatesector_root_item.find('updateconaddr')
    btdongleaddr_root.set('enable', cfg_data[22])
    btdongleaddr_root_item = btdongleaddr_root.find('btdongleaddr')
    btdongleaddr_root_item.find('LAP').text = cfg_data[15]
    btdongleaddr_root_item.find('UAP').text = cfg_data[16]
    btdongleaddr_root_item.find('NAP').text = cfg_data[17]
    updatecalib_root_item = updatesector_root_item.find('updatecalib')
    updatecalib_root_item.set('enable', cfg_data[23])
    chiptypestr = ''
    buf = (c_char * 20)()
    chiptype_len = get_dlddll().get_chiptype_value(buf)
    if chiptype_len is not 0:
        for i in range(chiptype_len):
            chiptypestr = chiptypestr + str(buf[i])

    if chiptypestr == '1400' or chiptypestr == '1501':
        updatecalib_root_item.find('defaultcalibval2').text = cfg_data[24]
    else:
        updatecalib_root_item.find('defaultcalibval').text = cfg_data[24]
    burn_root_item.find('hash1').text = cfg_data[25]
    burn_root_item.find('hash2').text = cfg_data[26]
    burn_root_item.find('app').text = cfg_data[27]
    burn_root_item.find('otaboot').text = cfg_data[28]
    burn_root_item.find('btfname').text = cfg_data[29]
    burn_root_item.find('chipver').text = cfg_data[30]
    custom1_root_item = burn_root_item.find('customer1')
    custom1_root_item.set('enable', cfg_data[31])
    custom1_root_item.find('customerpath').text = cfg_data[32]
    custom1_root_item.find('customeraddr').text = cfg_data[33]
    custom2_root_item = burn_root_item.find('customer2')
    custom2_root_item.set('enable', cfg_data[34])
    custom2_root_item.find('customerpath').text = cfg_data[35]
    custom2_root_item.find('customeraddr').text = cfg_data[36]
    custom3_root_item = burn_root_item.find('customer3')
    custom3_root_item.set('enable', cfg_data[37])
    custom3_root_item.find('customerpath').text = cfg_data[38]
    custom3_root_item.find('customeraddr').text = cfg_data[39]
    custom4_root_item = burn_root_item.find('customer4')
    custom4_root_item.set('enable', cfg_data[40])
    custom4_root_item.find('customerpath').text = cfg_data[41]
    custom4_root_item.find('customeraddr').text = cfg_data[42]
    updatesn_root_item = updatesector_root_item.find('updatesn')
    updatesn_root_item.find('sn_gen_type').text = cfg_data[43]
    updatesn_root_item.find('sn').text = cfg_data[44]
    updatesn_root_item.set('enable', cfg_data[45])
    burn_root_item.find('erasewhole').text = cfg_data[46]
    setmax_root_item = updatesector_root_item.find('max_num')
    setmax_root_item.set('enable', cfg_data[47])
    setmax_root_item.find('max_burn_num').text = cfg_data[48]
    if cfg_as_updatetool() is False:
        factorymode_root_item = root_parse.find('factorymode')
        factorymode_root_item.set('switch', cfg_data[49])
        factorymode_root_item.find('calibrate').text = cfg_data[50]
        factorymode_root_item.find('connector').text = cfg_data[51]
    doc_parse.write('productline_cfg.xml', xml_declaration=True)
    xml_doc_parse()
    bes_trace('save productline configure done.')


def xml_auto_gen_ble_addr_enable():
    global auto_gen_ble_addr_flag
    return auto_gen_ble_addr_flag


def xml_get_calibrate_cfg():
    global g_fctrmd_calib_switch
    return g_fctrmd_calib_switch


def xml_get_connector_cfg():
    global g_fctrmd_connector_switch
    return g_fctrmd_connector_switch


def xml_get_factorymode_cfg():
    global g_factorymode_switch
    return g_factorymode_switch


def xml_get_max_burn_num_enable():
    global g_max_num_enable
    if g_max_num_enable == '1':
        return 1
    return 0


def xml_get_update_sector_enable():
    global g_update_sector_enable
    return g_update_sector_enable


def xml_get_update_btaddr_enable():
    global g_update_btaddr_enable
    if g_update_btaddr_enable == '1':
        return 1
    return 0


def xml_get_update_btname_enable():
    global g_update_btname_enable
    if g_update_btname_enable == '1':
        return 1
    return 0


def xml_get_update_bleaddr_enable():
    global g_update_bleaddr_enable
    if g_update_bleaddr_enable == '1':
        return 1
    return 0


def xml_get_update_blename_enable():
    global g_update_blename_enable
    if g_update_blename_enable == '1':
        return 1
    return 0


def xml_get_update_conaddr_enable():
    global g_update_conaddr_enable
    if g_update_conaddr_enable == '1':
        return 1
    return 0


def xml_get_update_calib_enable():
    global g_update_calib_enable
    if g_update_calib_enable == '1':
        return 1
    return 0


def xml_get_fctrmd_btdongle_addr():
    global g_fctrmd_bt_dongle_addr
    return g_fctrmd_bt_dongle_addr


def xml_get_dev_localbtname():
    global g_dev_localbtname
    return g_dev_localbtname


def xml_get_dev_localblename():
    global g_dev_localblename
    return g_dev_localblename


def xml_encrypt_is_on():
    global g_encrypt_on
    return g_encrypt_on


def xml_get_customer_info():
    global g_chip_version
    global g_customer1_addr
    global g_customer1_enable
    global g_customer1_path
    global g_customer2_addr
    global g_customer2_enable
    global g_customer2_path
    global g_customer3_addr
    global g_customer3_enable
    global g_customer3_path
    global g_customer4_addr
    global g_customer4_enable
    global g_customer4_path
    return (
        g_chip_version, g_customer1_enable, g_customer1_path, g_customer1_addr, g_customer2_enable, g_customer2_path,
        g_customer2_addr, g_customer3_enable, g_customer3_path, g_customer3_addr, g_customer4_enable, g_customer4_path,
        g_customer4_addr)


def set_erase_info(en, length, addr):
    global g_erase_addr
    global g_erase_enable
    global g_erase_len
    g_erase_enable = en
    g_erase_len = length
    g_erase_addr = addr


def get_erase_info():
    return (
        g_erase_enable, g_erase_len, g_erase_addr)


def gen_random_optimize_bt_addr():
    verify_ret = -1
    enable = xml_get_update_sector_enable()
    assert enable != '1' and 0, 'error!'
    while verify_ret == -1:
        lap_uint = get_btaddr_lap_uint(xml_get_curr_bt_addr())
        verify_ret = get_dlddll().verify_lap_is_proper(lap_uint)
        if -1 == verify_ret:
            bt_addr_auto_increase()
        else:
            break

    lap_part1 = lap_uint & 16711680
    lap_part1 >>= 16
    lap_part2 = lap_uint & 65280
    lap_part2 >>= 8
    lap_part3 = lap_uint & 255
    ret_btaddr = copy.deepcopy(xml_get_curr_bt_addr())
    ret_btaddr[3] = lap_part3
    ret_btaddr[4] = lap_part2
    ret_btaddr[5] = lap_part1
    bt_addr_auto_increase()
    return ret_btaddr


def bt_addr_increase_2():
    enable = xml_get_update_sector_enable()
    if enable == '1':
        ret_addr_gen = xml_get_curr_bt_addr()
        low1_byte = ret_addr_gen[3]
        low2_byte = ret_addr_gen[4]
        low3_byte = ret_addr_gen[5]
        low3_byte = low3_byte + 2
        if low3_byte > 255:
            low3_byte = low3_byte - 256
            low2_byte = low2_byte + 1
            if low2_byte > 255:
                low2_byte = 0
                low1_byte = low1_byte + 1
                if low1_byte > 255:
                    low1_byte = 0
        ret_addr_gen[3] = low1_byte
        ret_addr_gen[4] = low2_byte
        ret_addr_gen[5] = low3_byte
        xml_set_curraddr(ret_addr_gen)
        return ret_addr_gen
    raise AssertionError


def bt_addr_auto_increase():
    enable = xml_get_update_sector_enable()
    if enable == '1':
        ret_addr_gen = xml_get_curr_bt_addr()
        low1_byte = ret_addr_gen[3]
        low2_byte = ret_addr_gen[4]
        low3_byte = ret_addr_gen[5]
        low3_byte = low3_byte + 1
        if low3_byte > 255:
            low3_byte = 0
            low2_byte = low2_byte + 1
            if low2_byte > 255:
                low2_byte = 0
                low1_byte = low1_byte + 1
                if low1_byte > 255:
                    low1_byte = 0
        ret_addr_gen[3] = low1_byte
        ret_addr_gen[4] = low2_byte
        ret_addr_gen[5] = low3_byte
        xml_set_curraddr(ret_addr_gen)
        return ret_addr_gen
    raise AssertionError


def ble_addr_increase_2():
    enable = xml_get_update_sector_enable()
    if enable == '1':
        curr_ble_addr_gen = xml_get_curr_ble_addr()
        low1_byte = curr_ble_addr_gen[3]
        low2_byte = curr_ble_addr_gen[4]
        low3_byte = curr_ble_addr_gen[5]
        low3_byte = low3_byte + 2
        if low3_byte > 255:
            low3_byte = low3_byte - 256
            low2_byte = low2_byte + 1
            if low2_byte > 255:
                low2_byte = 0
                low1_byte = low1_byte + 1
                if low1_byte > 255:
                    low1_byte = 0
        curr_ble_addr_gen[3] = low1_byte
        curr_ble_addr_gen[4] = low2_byte
        curr_ble_addr_gen[5] = low3_byte
        xml_update_ble_addr(curr_ble_addr_gen)
        return curr_ble_addr_gen
    if enable == '0':
        bes_trace('ENABLE BLE ADDR UPDATE @ XML.')
    else:
        raise AssertionError


def ble_addr_auto_increase():
    enable = xml_get_update_sector_enable()
    if enable == '1':
        curr_ble_addr_gen = xml_get_curr_ble_addr()
        low1_byte = curr_ble_addr_gen[3]
        low2_byte = curr_ble_addr_gen[4]
        low3_byte = curr_ble_addr_gen[5]
        low3_byte = low3_byte + 1
        if low3_byte > 255:
            low3_byte = 0
            low2_byte = low2_byte + 1
            if low2_byte > 255:
                low2_byte = 0
                low1_byte = low1_byte + 1
                if low1_byte > 255:
                    low1_byte = 0
        curr_ble_addr_gen[3] = low1_byte
        curr_ble_addr_gen[4] = low2_byte
        curr_ble_addr_gen[5] = low3_byte
        xml_update_ble_addr(curr_ble_addr_gen)
        return curr_ble_addr_gen
    if enable == '0':
        bes_trace('ENABLE BLE ADDR UPDATE @ XML.')
    else:
        raise AssertionError


def xml_doc_write():
    global currbleaddr_root
    global currbtaddr_root
    global g_setmax_root
    global g_update_sn_root
    bt_write_flag = xml_get_update_sector_enable()
    if bt_write_flag == '1':
        bt_addr_text = ''
        temp_bt_addr_gen = xml_get_curr_bt_addr()
        bt_addr_text += '0x%.02x' % temp_bt_addr_gen[3]
        bt_addr_text += ','
        bt_addr_text += '0x%.02x' % temp_bt_addr_gen[4]
        bt_addr_text += ','
        bt_addr_text += '0x%.02x' % temp_bt_addr_gen[5]
        currbtaddr_root.find('LAP').text = bt_addr_text
        ble_addr_text = ''
        temp_ble_addr_gen = xml_get_curr_ble_addr()
        ble_addr_text += '0x%.02x' % temp_ble_addr_gen[3]
        ble_addr_text += ','
        ble_addr_text += '0x%.02x' % temp_ble_addr_gen[4]
        ble_addr_text += ','
        ble_addr_text += '0x%.02x' % temp_ble_addr_gen[5]
        currbleaddr_root.find('LAP').text = ble_addr_text
        rest_burn_num = get_rest_burn_num()
        g_setmax_root.find('max_burn_num').text = str(rest_burn_num)
        unuse_btaddr = xml_get_failed_bt_addr()
        unuse_btaddr_num = len(unuse_btaddr)
        if unuse_btaddr_num > 0:
            unuse_bt_addr_text = ''
            for i in range(0, len(unuse_btaddr)):
                unuse_bt_addr_text = unuse_bt_addr_text + unuse_btaddr[i] + ';'

            unuse_bt_addr_text = unuse_bt_addr_text[:-1]
            root_parse.find('unuse_bt_addr').text = unuse_bt_addr_text
        else:
            root_parse.find('unuse_bt_addr').text = ''
        unuse_bleaddr = xml_get_failed_ble_addr()
        unuse_bleaddr_num = len(unuse_bleaddr)
        if unuse_bleaddr_num > 0:
            unuse_ble_addr_text = ''
            for i in range(0, len(unuse_bleaddr)):
                unuse_ble_addr_text = unuse_ble_addr_text + unuse_bleaddr[i] + ';'

            unuse_ble_addr_text = unuse_ble_addr_text[:-1]
            root_parse.find('unuse_ble_addr').text = unuse_ble_addr_text
        else:
            root_parse.find('unuse_ble_addr').text = ''
        curr_sn = xml_get_curr_sn()
        g_update_sn_root.find('sn').text = curr_sn
        doc_parse.write('productline_cfg.xml', xml_declaration=True)


def xml_dev_local_name_write_back(bt_name):
    """write bt_name back to product"""
    global g_dev_localbtname
    root_parse = doc_parse.getroot()
    burn_root_item = root_parse.find('burn')
    updatesector_root_item = burn_root_item.find('updatesector')
    updatebtname_root = updatesector_root_item.find('updatebtname')
    updatebtname_root.find('dev_localname').text = bt_name
    g_dev_localbtname = bt_name
    doc_parse.write('productline_cfg.xml', xml_declaration=True)


def xml_get_encrypt_on():
    try:
        docparse = Et.parse('productline_cfg.xml')
    except:
        return False

    rootparse = docparse.getroot()
    if rootparse.find('encrypt_on').text == '1':
        encrypt_on = True
    else:
        encrypt_on = False
    return encrypt_on


def xml_mod_for_encrypt_mode():
    try:
        docparse = Et.parse('productline_cfg.xml')      # 解析productline_cfg文件
    except Exception as e:
        return e

    root_parse = docparse.getroot()
    burn_root = root_parse.find('burn')
    updatesector_root_item = burn_root.find('updatesector')
    updatesector_root_item.set('enable', '1')
    updatesector_root_item.find('addr_gen_type').text = '1'
    updatebtaddr_root = updatesector_root_item.find('updatebtaddr')
    updatebtaddr_root.set('enable', '1')
    updatebtname_root = updatesector_root_item.find('updatebtname')
    updatebtname_root.set('enable', '1')
    updatebleaddr_root = updatesector_root_item.find('updatebleaddr')
    updatebleaddr_root.set('enable', '1')
    btdongleaddr_root = updatesector_root_item.find('updateconaddr')
    btdongleaddr_root.set('enable', '1')
    updatecalib_root = updatesector_root_item.find('updatecalib')
    updatecalib_root.set('enable', '1')
    updateblename_root = updatesector_root_item.find('updateblename')
    updateblename_root.set('enable', '1')
    docparse.write('productline_cfg.xml', xml_declaration=True)


def xml_doc_parse():
    global curr_ble_addr_gen
    global curr_bt_addr_gen
    global currbleaddr_root
    global currbtaddr_root
    global default_calib_value
    global default_calib_value2
    global doc_parse
    global g_app_switch
    global g_baudrate
    global g_btfname_switch
    global g_burnandfactorymode_switch
    global g_burnappota_only
    global g_burn_path_1
    global g_burn_path_2
    global g_cfgasupdate_flag
    global g_chip_version
    global g_customer1_addr
    global g_customer1_enable
    global g_customer1_path
    global g_customer2_addr
    global g_customer2_enable
    global g_customer2_path
    global g_customer3_addr
    global g_customer3_enable
    global g_customer3_path
    global g_customer4_addr
    global g_customer4_enable
    global g_customer4_path
    global g_dev_localblename
    global g_dev_localbtname
    global g_dld_complete_count
    global g_dld_failure_count
    global g_dldresult_root
    global g_encrypt_on
    global g_erasewhole_switch
    global g_factorymode_switch
    global g_fctrmd_bt_dongle_addr
    global g_fctrmd_calib_switch
    global g_fctrmd_connector_switch
    global g_language_cfg
    global g_max_num_enable
    global g_onlyburn_switch
    global g_onlyfactorymode_switch
    global g_otaboot_switch
    global g_setmax_root
    global g_sn
    global g_update_Customized_Addr
    global g_update_Customized_enable
    global g_update_bleaddr_enable
    global g_update_blename_enable
    global g_update_btaddr_enable
    global g_update_btname_enable
    global g_update_calib_enable
    global g_update_conaddr_enable
    global g_update_sector_enable
    global g_update_sn_enable
    global g_update_sn_root
    global g_verify_text_1
    global g_verify_text_2
    global g_verifycrc1_switch
    global g_verifycrc2_switch
    global root_parse
    global g_delay_time
    try:
        doc_parse = Et.parse('productline_cfg.xml')
    except:
        return 'can not parse productline_cfg.xml.'

    root_parse = doc_parse.getroot()
    g_language_cfg = root_parse.find('language').text
    g_cfgasupdate_flag = root_parse.find('cfgasupdate').text
    g_burnappota_only = root_parse.find('burnappota_only').text
    g_baudrate = root_parse.find('baudrate').text
    g_delay_time = root_parse.find('delay_time').text
    if root_parse.find('encrypt_on').text == '1':
        g_encrypt_on = True
    else:
        g_encrypt_on = False
    burn_root = root_parse.find('burn')
    burn_switch = burn_root.get('switch')
    fctrmd_root = root_parse.find('factorymode')
    g_factorymode_switch = fctrmd_root.get('switch')
    cfgmode_list = []
    cfgmode_list.append(burn_switch)
    cfgmode_list.append(g_factorymode_switch)
    if cfgmode_list != ['1', '0'] and cfgmode_list != ['0', '1'] and cfgmode_list != ['1', '1']:
        return 'burn or factorymode switch cfg error.'
    else:
        g_app_switch = burn_root.find('app').text
        g_burn_path_1 = burn_root.find('burnpath_1').text
        g_verifycrc1_switch = burn_root.find('hash1').text
        g_verify_text_1 = burn_root.find('verify_hash_1').text
        g_otaboot_switch = burn_root.find('otaboot').text
        g_burn_path_2 = burn_root.find('burnpath_2').text
        g_verifycrc2_switch = burn_root.find('hash2').text
        g_verify_text_2 = burn_root.find('verify_hash_2').text
        g_btfname_switch = burn_root.find('btfname').text
        g_erasewhole_switch = burn_root.find('erasewhole').text
        update_sector_root = burn_root.find('updatesector')
        g_update_sector_enable = update_sector_root.get('enable')
        addr_gen_type = update_sector_root.find('addr_gen_type').text
        set_device_address_gen_type(int(addr_gen_type))
        g_setmax_root = update_sector_root.find('max_num')
        g_max_num_enable = g_setmax_root.get('enable')
        max_burn_num = g_setmax_root.find('max_burn_num').text
        set_rest_burn_num(int(max_burn_num))
        update_btaddr_root = update_sector_root.find('updatebtaddr')
        g_update_btaddr_enable = update_btaddr_root.get('enable')
        currbtaddr_root = update_btaddr_root.find('curr_bt_addr_gen')
        nap_currbtaddr = currbtaddr_root.find('NAP').text
        uap_currbtaddr = currbtaddr_root.find('UAP').text
        lap_currbtaddr = currbtaddr_root.find('LAP').text
        list_curraddr = nap_currbtaddr + ',' + uap_currbtaddr + ',' + lap_currbtaddr
        curr_bt_addr_gen = list(eval(list_curraddr))
        update_btname_root = update_sector_root.find('updatebtname')
        g_update_btname_enable = update_btname_root.get('enable')
        g_dev_localbtname = update_btname_root.find('dev_localname').text.rstrip()
        update_bleaddr_root = update_sector_root.find('updatebleaddr')
        g_update_bleaddr_enable = update_bleaddr_root.get('enable')
        currbleaddr_root = update_bleaddr_root.find('curr_ble_addr_gen')
        nap_currbleaddr = currbleaddr_root.find('NAP').text
        uap_currbleaddr = currbleaddr_root.find('UAP').text
        lap_currbleaddr = currbleaddr_root.find('LAP').text
        str_currble_addr = nap_currbleaddr + ',' + uap_currbleaddr + ',' + lap_currbleaddr
        curr_ble_addr_gen = list(eval(str_currble_addr))
        update_blename_root = update_sector_root.find('updateblename')
        g_update_blename_enable = update_blename_root.get('enable')
        g_dev_localblename = update_blename_root.find('dev_localname').text.rstrip()
        update_calib_root = update_sector_root.find('updatecalib')
        g_update_calib_enable = update_calib_root.get('enable')
        default_calib_text = update_calib_root.find('defaultcalibval').text
        default_calib_value = int(default_calib_text, 10)
        default_calib_text2 = update_calib_root.find('defaultcalibval2').text
        default_calib_value2 = int(default_calib_text2, 10)
        update_conaddr_root = update_sector_root.find('updateconaddr')
        g_update_conaddr_enable = update_conaddr_root.get('enable')
        bt_dongle_root = update_conaddr_root.find('btdongleaddr')
        nap_btdongle = bt_dongle_root.find('NAP').text
        uap_btdongle = bt_dongle_root.find('UAP').text
        lap_btdongle = bt_dongle_root.find('LAP').text
        str_btdongle_addr = nap_btdongle + ',' + uap_btdongle + ',' + lap_btdongle
        g_fctrmd_bt_dongle_addr = list(eval(str_btdongle_addr))
        g_update_sn_root = update_sector_root.find('updatesn')
        g_update_sn_enable = g_update_sn_root.get('enable')
        sn_gen_type = int(g_update_sn_root.find('sn_gen_type').text)
        set_sn_gen_type(int(sn_gen_type))
        g_sn = g_update_sn_root.find('sn').text
        Customized_root = burn_root.find('Customized')
        g_update_Customized_enable = Customized_root.get('enable')
        g_update_Customized_Addr = Customized_root.find('Addr').text
        g_chip_version = burn_root.find('chipver').text
        customer1_root = burn_root.find('customer1')
        g_customer1_enable = customer1_root.get('enable')
        g_customer1_path = customer1_root.find('customerpath').text
        g_customer1_addr = customer1_root.find('customeraddr').text
        customer2_root = burn_root.find('customer2')
        g_customer2_enable = customer2_root.get('enable')
        g_customer2_path = customer2_root.find('customerpath').text
        g_customer2_addr = customer2_root.find('customeraddr').text
        customer3_root = burn_root.find('customer3')
        g_customer3_enable = customer3_root.get('enable')
        g_customer3_path = customer3_root.find('customerpath').text
        g_customer3_addr = customer3_root.find('customeraddr').text
        customer4_root = burn_root.find('customer4')
        g_customer4_enable = customer4_root.get('enable')
        g_customer4_path = customer4_root.find('customerpath').text
        g_customer4_addr = customer4_root.find('customeraddr').text
        if g_factorymode_switch == '1':
            g_fctrmd_calib_switch = fctrmd_root.find('calibrate').text
            g_fctrmd_connector_switch = fctrmd_root.find('connector').text
            if g_fctrmd_connector_switch != '0' and g_fctrmd_connector_switch != '1':
                return 'productline_cfg.xml cfg error(connector)'
            if g_fctrmd_calib_switch != '0' and g_fctrmd_calib_switch != '1':
                return 'productline_cfg.xml cfg error(calibrate)'
            if g_fctrmd_connector_switch == '0' and g_fctrmd_calib_switch == '0':
                return 'productline_cfg.xml cfg error(factorymode)'
        else:
            g_fctrmd_calib_switch = '0'
            g_fctrmd_connector_switch = '0'
        if cfgmode_list == ['1', '0']:
            g_onlyburn_switch = True
            g_onlyfactorymode_switch = False
            g_burnandfactorymode_switch = False
        elif cfgmode_list == ['0', '1']:
            g_onlyburn_switch = False
            g_onlyfactorymode_switch = True
            g_burnandfactorymode_switch = False
        elif cfgmode_list == ['1', '1']:
            g_onlyburn_switch = False
            g_onlyfactorymode_switch = False
            g_burnandfactorymode_switch = True
        g_dldresult_root = root_parse.find('dld_result')
        complete_text = g_dldresult_root.find('complete').text
        g_dld_complete_count = int(complete_text)
        failure_text = g_dldresult_root.find('failure').text
        g_dld_failure_count = int(failure_text)
        unuse_btaddr_str = root_parse.find('unuse_bt_addr').text
        if unuse_btaddr_str != '' and unuse_btaddr_str != None:
            unuse_btaddr = unuse_btaddr_str.split(';')
            xml_set_failed_bt_addr(unuse_btaddr)
        unuse_bleaddr_str = root_parse.find('unuse_ble_addr').text
        if unuse_bleaddr_str != '' and unuse_bleaddr_str != None:
            unuse_bleaddr = unuse_bleaddr_str.split(';')
            xml_set_failed_ble_addr(unuse_bleaddr)
        set_g_efuseID1(int(root_parse.find('efuse_ID1').text))
        set_g_efuseID2(int(root_parse.find('efuse_ID2').text))
        return 'xmlcfgok'


def get_dldresult_root():
    return g_dldresult_root


def restore_dldresult_to_xml():
    complete_count, failure_count = get_dld_result()
    g_dldresult_root.find('complete').text = str(complete_count)
    g_dldresult_root.find('failure').text = str(failure_count)
    doc_parse.write('productline_cfg.xml', xml_declaration=True)


def dld_complete_count_increase():
    global g_dld_complete_count
    g_dld_complete_count += 1


def dld_failure_count_increase():
    global g_dld_failure_count
    g_dld_failure_count += 1


def get_dld_result():
    return (
        g_dld_complete_count, g_dld_failure_count)


def reset_dld_result():
    global g_dld_complete_count
    global g_dld_failure_count
    g_dld_complete_count = 0
    g_dld_failure_count = 0


def write_cfg_log(dev_bt_addr, dev_ble_addr, calib_value, sn):
    factory_mode_only = xml_getxmlcfg_is_fctrmdonly()
    if factory_mode_only:
        log_text = '------------------START TO TEST---------------------- \n'
        save_log_to_file(log_text)
        log_text = 'WAIT FOR CHIP POWER ON\n\n'
        save_log_to_file(log_text)
        return
    update_sector_switch = xml_get_update_sector_enable()
    localname = xml_get_dev_localbtname()
    if xml_get_update_calib_enable() == '0':
        calib_value_str = "needn't write"
    else:
        calib_value_str = str(calib_value)
    log_text = '------------------START TO BURN---------------------- \n'
    save_log_to_file(log_text)
    log_text = ''
    if update_sector_switch == '1':
        log_text += localname
        log_text += '    btaddr:'
        log_text += dev_bt_addr
        log_text += '    '
        log_text += '    bleaddr:'
        log_text += dev_ble_addr
        log_text += '    '
        log_text += '    sn:'
        log_text += sn
        log_text += '    '
        log_text += '     calibvalue:'
        log_text += calib_value_str
        log_text += '    '
    else:
        log_text += "needn't update factory sector  "
    log_text += '\n'
    save_log_to_file(log_text)
    log_text = 'WAIT FOR CHIP POWER ON\n\n'
    save_log_to_file(log_text)


def sn_grow():
    """suppose the curr_sn is valid, AAAABBCDEEFabcde, abcde + 1 == abcdf
            return AAAABBCDEEFabcdf"""
    curr_sn = xml_get_curr_sn()
    sn_str = curr_sn[-6:]
    grow_dict = {'0': '1',
                 '1': '2', '2': '3', '3': '4', '4': '5', '5': '6', '6': '7', '7': '8', '8': '9', '9': '0'}
    reverse_str = []
    reverse_str.append(grow_dict[sn_str[5]])
    if sn_str[5] != '9':
        reverse_str.append(sn_str[4])
        reverse_str.append(sn_str[3])
        reverse_str.append(sn_str[2])
        reverse_str.append(sn_str[1])
        reverse_str.append(sn_str[0])
    else:
        reverse_str.append(grow_dict[sn_str[4]])
        if sn_str[4] != '9':
            reverse_str.append(sn_str[3])
            reverse_str.append(sn_str[2])
            reverse_str.append(sn_str[1])
            reverse_str.append(sn_str[0])
        else:
            reverse_str.append(grow_dict[sn_str[3]])
            if sn_str[3] != '9':
                reverse_str.append(sn_str[2])
                reverse_str.append(sn_str[1])
                reverse_str.append(sn_str[0])
            else:
                reverse_str.append(grow_dict[sn_str[2]])
                if sn_str[2] != '9':
                    reverse_str.append(sn_str[1])
                    reverse_str.append(sn_str[0])
                else:
                    reverse_str.append(grow_dict[sn_str[1]])
                    if sn_str[1] != '9':
                        reverse_str.append(sn_str[0])
                    else:
                        reverse_str.append(grow_dict[sn_str[0]])
    ret_str = copy.deepcopy(
        curr_sn[0:10].upper() + reverse_str[5] + reverse_str[4] + reverse_str[3] + reverse_str[2] + reverse_str[1] +
        reverse_str[0])
    xml_set_curr_sn(ret_str)
    return ret_str


def dld_sector_gen(bin_name, addr_inc_flag):
    f_path = os.getcwd() + '\\bin\\' + bin_name
    calib_value = xml_getxmlcfg_default_calib_value()
    update_sector_enable = xml_get_update_sector_enable()
    if update_sector_enable == '0':
        dev_bt_addr = xml_get_curr_bt_addr()
        dev_ble_addr = xml_get_curr_ble_addr()
        sn = xml_get_curr_sn()
        get_dlddll().userdata_sector_gen(f_path)
        return (
            dev_bt_addr, dev_ble_addr, calib_value, sn)
    else:
        threads_mutex = get_mainproc_monitor_mutex()
        threads_mutex.acquire()
        address_gen_type = get_device_address_gen_type()
        if address_gen_type == 0:
            if addr_inc_flag is True:
                if xml_get_update_btaddr_enable() == 0 and xml_get_update_bleaddr_enable() == 0:
                    dev_bt_addr = xml_get_curr_bt_addr()
                    dev_ble_addr = xml_get_curr_ble_addr()
                else:
                    if xml_get_update_btaddr_enable() == 1:
                        unuse_btaddr = xml_get_failed_bt_addr()
                        if len(unuse_btaddr) != 0:
                            dev_bt_addr_str = unuse_btaddr[0]
                            dev_btaddr_list = dev_bt_addr_str.split(':')
                            dev_bt_addr = []
                            for i in range(0, len(dev_btaddr_list)):
                                dev_btaddr_list[i] = '0x' + dev_btaddr_list[i]
                                dev_bt_addr.append(eval(dev_btaddr_list[i]))

                            del unuse_btaddr[0]
                            xml_set_failed_bt_addr(unuse_btaddr)
                        else:
                            dev_bt_addr = gen_random_optimize_bt_addr()
                        dev_bt_addr_str = '%02X:%02X:%02X:%02X:%02X:%02X' % (dev_bt_addr[0],
                                                                             dev_bt_addr[1],
                                                                             dev_bt_addr[2],
                                                                             dev_bt_addr[3],
                                                                             dev_bt_addr[4],
                                                                             dev_bt_addr[5])
                        using_bt_addr = get_using_bt_addr()
                        using_bt_addr.append(dev_bt_addr_str)
                        using_bt_addr = list(set(using_bt_addr))
                        set_using_bt_addr(using_bt_addr)
                    else:
                        dev_bt_addr = xml_get_curr_bt_addr()
                    if xml_get_update_bleaddr_enable() == 1:
                        unuse_bleaddr = xml_get_failed_ble_addr()
                        if len(unuse_bleaddr) != 0:
                            dev_ble_addr = []
                            dev_ble_addr_str = unuse_bleaddr[0]
                            dev_bleaddr_list = dev_ble_addr_str.split(':')
                            for i in range(0, len(dev_bleaddr_list)):
                                dev_bleaddr_list[i] = '0x' + dev_bleaddr_list[i]
                                dev_ble_addr.append(eval(dev_bleaddr_list[i]))

                            del unuse_bleaddr[0]
                            xml_set_failed_ble_addr(unuse_bleaddr)
                        else:
                            dev_ble_addr = ble_addr_auto_increase()
                        dev_ble_addr_str = '%02X:%02X:%02X:%02X:%02X:%02X' % (dev_ble_addr[0],
                                                                              dev_ble_addr[1],
                                                                              dev_ble_addr[2],
                                                                              dev_ble_addr[3],
                                                                              dev_ble_addr[4],
                                                                              dev_ble_addr[5])
                        using_ble_addr = get_using_ble_addr()
                        using_ble_addr.append(dev_ble_addr_str)
                        using_ble_addr = list(set(using_ble_addr))
                        set_using_ble_addr(using_ble_addr)
                    else:
                        dev_ble_addr = xml_get_curr_ble_addr()
                    xml_doc_write()
            else:
                dev_bt_addr = xml_get_curr_bt_addr()
                dev_ble_addr = xml_get_curr_ble_addr()
        elif address_gen_type == 1:
            if addr_inc_flag is True:
                if xml_get_update_btaddr_enable() == 0 and xml_get_update_bleaddr_enable() == 0:
                    dev_bt_addr = xml_get_curr_bt_addr()
                    dev_ble_addr = xml_get_curr_ble_addr()
                else:
                    if xml_get_update_btaddr_enable() == 1:
                        unuse_btaddr = xml_get_failed_bt_addr()
                        if len(unuse_btaddr) != 0:
                            dev_bt_addr_str = unuse_btaddr[0]
                            dev_btaddr_list = dev_bt_addr_str.split(':')
                            dev_bt_addr = []
                            for i in range(0, len(dev_btaddr_list)):
                                dev_btaddr_list[i] = '0x' + dev_btaddr_list[i]
                                dev_bt_addr.append(eval(dev_btaddr_list[i]))

                            del unuse_btaddr[0]
                            xml_set_failed_bt_addr(unuse_btaddr)
                        else:
                            dev_bt_addr = bt_addr_auto_increase()
                        dev_bt_addr_str = '%02X:%02X:%02X:%02X:%02X:%02X' % (dev_bt_addr[0],
                                                                             dev_bt_addr[1],
                                                                             dev_bt_addr[2],
                                                                             dev_bt_addr[3],
                                                                             dev_bt_addr[4],
                                                                             dev_bt_addr[5])
                        using_bt_addr = get_using_bt_addr()
                        using_bt_addr.append(dev_bt_addr_str)
                        using_bt_addr = list(set(using_bt_addr))
                        set_using_bt_addr(using_bt_addr)
                    else:
                        dev_bt_addr = xml_get_curr_bt_addr()
                    if xml_get_update_bleaddr_enable() == 1:
                        unuse_bleaddr = xml_get_failed_ble_addr()
                        if len(unuse_bleaddr) != 0:
                            dev_ble_addr = []
                            dev_ble_addr_str = unuse_bleaddr[0]
                            dev_bleaddr_list = dev_ble_addr_str.split(':')
                            for i in range(0, len(dev_bleaddr_list)):
                                dev_bleaddr_list[i] = '0x' + dev_bleaddr_list[i]
                                dev_ble_addr.append(eval(dev_bleaddr_list[i]))

                            del unuse_bleaddr[0]
                            xml_set_failed_ble_addr(unuse_bleaddr)
                        else:
                            dev_ble_addr = ble_addr_auto_increase()
                        dev_ble_addr_str = '%02X:%02X:%02X:%02X:%02X:%02X' % (dev_ble_addr[0],
                                                                              dev_ble_addr[1],
                                                                              dev_ble_addr[2],
                                                                              dev_ble_addr[3],
                                                                              dev_ble_addr[4],
                                                                              dev_ble_addr[5])
                        using_ble_addr = get_using_ble_addr()
                        using_ble_addr.append(dev_ble_addr_str)
                        using_ble_addr = list(set(using_ble_addr))
                        set_using_ble_addr(using_ble_addr)
                    else:
                        dev_ble_addr = xml_get_curr_ble_addr()
                    xml_doc_write()
            else:
                dev_bt_addr = xml_get_curr_bt_addr()
                dev_ble_addr = xml_get_curr_ble_addr()
        elif address_gen_type == 2:
            if addr_inc_flag is True:
                if xml_get_update_btaddr_enable() == 0 and xml_get_update_bleaddr_enable() == 0:
                    dev_bt_addr = xml_get_curr_bt_addr()
                    dev_ble_addr = xml_get_curr_ble_addr()
                else:
                    if xml_get_update_btaddr_enable() == 1:
                        unuse_btaddr = xml_get_failed_bt_addr()
                        if len(unuse_btaddr) != 0:
                            dev_bt_addr_str = unuse_btaddr[0]
                            dev_btaddr_list = dev_bt_addr_str.split(':')
                            dev_bt_addr = []
                            for i in range(0, len(dev_btaddr_list)):
                                dev_btaddr_list[i] = '0x' + dev_btaddr_list[i]
                                dev_bt_addr.append(eval(dev_btaddr_list[i]))

                            del unuse_btaddr[0]
                            xml_set_failed_bt_addr(unuse_btaddr)
                        else:
                            dev_bt_addr = bt_addr_increase_2()
                        dev_bt_addr_str = '%02X:%02X:%02X:%02X:%02X:%02X' % (dev_bt_addr[0],
                                                                             dev_bt_addr[1],
                                                                             dev_bt_addr[2],
                                                                             dev_bt_addr[3],
                                                                             dev_bt_addr[4],
                                                                             dev_bt_addr[5])
                        using_bt_addr = get_using_bt_addr()
                        using_bt_addr.append(dev_bt_addr_str)
                        using_bt_addr = list(set(using_bt_addr))
                        set_using_bt_addr(using_bt_addr)
                    else:
                        dev_bt_addr = xml_get_curr_bt_addr()
                    if xml_get_update_bleaddr_enable() == 1:
                        unuse_bleaddr = xml_get_failed_ble_addr()
                        if len(unuse_bleaddr) != 0:
                            dev_ble_addr = []
                            dev_ble_addr_str = unuse_bleaddr[0]
                            dev_bleaddr_list = dev_ble_addr_str.split(':')
                            for i in range(0, len(dev_bleaddr_list)):
                                dev_bleaddr_list[i] = '0x' + dev_bleaddr_list[i]
                                dev_ble_addr.append(eval(dev_bleaddr_list[i]))

                            del unuse_bleaddr[0]
                            xml_set_failed_ble_addr(unuse_bleaddr)
                        else:
                            dev_ble_addr = ble_addr_increase_2()
                        dev_ble_addr_str = '%02X:%02X:%02X:%02X:%02X:%02X' % (dev_ble_addr[0],
                                                                              dev_ble_addr[1],
                                                                              dev_ble_addr[2],
                                                                              dev_ble_addr[3],
                                                                              dev_ble_addr[4],
                                                                              dev_ble_addr[5])
                        using_ble_addr = get_using_ble_addr()
                        using_ble_addr.append(dev_ble_addr_str)
                        using_ble_addr = list(set(using_ble_addr))
                        set_using_ble_addr(using_ble_addr)
                    else:
                        dev_ble_addr = xml_get_curr_ble_addr()
                    xml_doc_write()
            else:
                dev_bt_addr = xml_get_curr_bt_addr()
                dev_ble_addr = xml_get_curr_ble_addr()
        else:
            dev_bt_addr = xml_get_curr_bt_addr()
            dev_ble_addr = xml_get_curr_ble_addr()
        dongle_addr = xml_get_fctrmd_btdongle_addr()
        bt_addr_pack = struct.pack('<6B', dev_bt_addr[5], dev_bt_addr[4], dev_bt_addr[3], dev_bt_addr[2], dev_bt_addr[1],
                                   dev_bt_addr[0])
        ble_addr_pack = struct.pack('<6B', dev_ble_addr[5], dev_ble_addr[4], dev_ble_addr[3], dev_ble_addr[2],
                                    dev_ble_addr[1], dev_ble_addr[0])
        dongle_addr_pack = struct.pack('<6B', dongle_addr[5], dongle_addr[4], dongle_addr[3], dongle_addr[2], dongle_addr[1],
                                       dongle_addr[0])
        if xml_get_dev_localbtname() is None:
            bt_name = 'WtRockBox'
        else:
            bt_name = xml_get_dev_localbtname()
        if xml_get_dev_localblename() is None:
            ble_name = ''
        else:
            ble_name = xml_get_dev_localblename()
        sn_gen_type = xml_get_sn_gen_type()
        if sn_gen_type == 0 and xml_get_update_sn_enable() == 1:
            sn = sn_grow()
            xml_doc_write()
        else:
            sn = xml_get_curr_sn()
        get_dlddll().sector_gen(f_path, bt_addr_pack, ble_addr_pack, dongle_addr_pack, bt_name, ble_name, calib_value)
        threads_mutex.release()
        return dev_bt_addr, dev_ble_addr, calib_value, sn
