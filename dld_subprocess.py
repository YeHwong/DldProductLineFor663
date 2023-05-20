#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2023-02-17 14:26:18
# @File: dld_subprocess.py
# @Author: YeHwong
# @Email: 598316810@qq.com
# @Version ：1.1.0
# 修复烧录OTA BOOT失败BUG
import copy
import multiprocessing
import struct
from ctypes import *
import ctypes
import serial

from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from cryptography.hazmat.primitives.hashes import SHA256

from dld_global import *
from dld_global import GlobModule
from PyQt5.Qt import QObject


class dld_thread(threading.Thread):
    """
        升级进程类
    """
    def __init__(self, job, com, sector_update_flag, connector_switch, calib_switch, cfg_as_update,
                 burn_field_enable_value, custom_bin_list, load_dll, encrypt_on, eraser_switch, customized_enable,
                 customized_addr):
        """
                升级进程类

        :param job:  升级工作状态列表集
        :type job: list
        :param com: 串口号
        :type com:  str
        :param sector_update_flag: 分区写入启用标志
        :type sector_update_flag: bool
        :param connector_switch:
        :type connector_switch:
        :param calib_switch: 校准启用标志
        :type calib_switch: bool
        :param cfg_as_update:
        :type cfg_as_update:
        :param burn_field_enable_value:
        :type burn_field_enable_value:
        :param custom_bin_list:
        :type custom_bin_list:
        :param load_dll:
        :type load_dll:
        :param encrypt_on: 加密模式打开？
        :type encrypt_on: str
        :param eraser_switch:
        :type eraser_switch:
        :param customized_enable:
        :type customized_enable:
        :param customized_addr:
        :type customized_addr:
        """
        threading.Thread.__init__(self)
        self.job = job
        self.com = str(com)
        self.stopped = False
        self.r_file = ''
        self.f_file = ''
        self.fb_file = ''
        self.app_switch = False
        self.boot_switch = False
        self.argc = 0
        self.argv = []
        self.sector_update_flag = sector_update_flag
        self.calib_switch = calib_switch
        self.connector_switch = connector_switch
        self.cfg_as_update = cfg_as_update
        self.burn_field_enable_value = burn_field_enable_value
        self.custom_bin_list = custom_bin_list
        self.dldtool = load_dll
        self.encrypt_on = encrypt_on
        self.eraser_switch = eraser_switch
        self.customized_enable = customized_enable
        self.customized_addr = customized_addr

    def dispatch_pip_msg_terminated(self):
        """dispatch_pip_msg_terminated"""
        self.job['childconn'].send(['ev_wm_terminated'])

    def thread_communicate_with_chip_evt_dispatch(self, evt):
        """dispatch evt from dld thread"""
        str_leave = 'leaving'
        str_loop = 'looping'
        if evt == ev_wm_burn_progress:
            progress = self.dldtool.get_burn_progress()
            self.job['childconn'].send(['ev_wm_burn_progress', int(progress)])
        elif evt == ev_wm_sync_succeed:
            self.job['childconn'].send(['ev_wm_sync_succeed'])
        elif evt == ev_wm_run_programmer_succeed:
            bes_trace('evt ev_wm_run_programmer_succeed')
        elif evt == ev_wm_bin_encrypt_begin:
            efuse_value1 = self.dldtool.get_encrypt_efuse_value1()
            efuse_value2 = self.dldtool.get_encrypt_efuse_value2()
            efuse_value = efuse_value1 | efuse_value2 << 16
            pack_efuse_data = struct.pack('i', efuse_value)
            ret_data = get_tool_rsa_key()
            ret_descrip = ret_data[0]
            if ret_descrip == 'password_incorrect':
                self.job['childconn'].send(['ev_wm_bin_encrypt_begin', ret_descrip])
            elif ret_descrip == 'succeed':
                pri_key = ret_data[1][0]
                pub_key = ret_data[1][1]
                signer = Signature_pkcs1_v1_5.new(pri_key)
                digest = SHA256.new()
                digest.update(pack_efuse_data + dld_courier.encrypt_data)
                sign = signer.sign(digest)
                dump_pubkey = GlobModule.dump_public_key(pub_key)
                key_addr_int = self.dldtool.get_key_addr_from_buildinfo(self.job['encrypt_path'])
                if key_addr_int != 0:
                    GlobModule.add_pubkey_signature_to_bin(self.job['encrypt_path'], key_addr_int, dump_pubkey, sign)
                self.dldtool.end_encrypt_block()
        elif evt == ev_wm_bin_encrypt_end:
            bes_trace('ev_wm_bin_encrypt_end')

        elif evt == ev_wm_burn_magic:
            self.job['childconn'].send(['ev_wm_burn_magic'])
        elif evt == ev_wm_burn_failure:
            errorcode = self.dldtool.get_exit_code()
            self.job['childconn'].send(['ev_wm_burn_failure', errorcode])
        elif evt == ev_wm_burn_complt:
            self.job['childconn'].send(['ev_wm_burn_complt'])
        elif evt == ev_wm_chip_power_off:
            self.job['childconn'].send(['ev_wm_chip_power_off'])
        elif evt == ev_wm_burn_efuse_start:
            self.job['childconn'].send(['ev_wm_burn_efuse_start'])
        elif evt == ev_wm_burn_efuse_end:
            self.job['childconn'].send(['ev_wm_burn_efuse_end'])
        else:
            if evt == ev_wm_exit_valid:
                self.job['childconn'].send(['ev_wm_exit_valid'])
                return str_leave
            if evt == ev_wm_exit_invalid:
                errorcode = self.dldtool.get_exit_code()
                self.job['childconn'].send(['ev_wm_exit_invalid', errorcode])
                return str_leave
            if evt == ev_wm_exit_user_stop:
                return str_leave
            if evt == ev_wm_sync_wait:
                bes_trace('waiting for chip sync...')
            elif evt == ev_wm_port_open_succeed:
                bes_trace('port open succeed')
            elif evt == ev_wm_factory_mode:
                self.job['childconn'].send(['ev_wm_factory_mode'])
            elif evt == ev_wm_factory_mode_progress:
                progress = self.dldtool.pyext_get_mcu_test_progress()
                self.job['childconn'].send(['ev_wm_factory_mode_progress', int(progress)])
            elif evt == ev_wm_factory_calib_value:
                calib_value = self.dldtool.pyext_get_calib_value()
                self.job['childconn'].send(['ev_wm_factory_calib_value', calib_value])
            elif evt == ev_wm_factory_mode_success:
                self.job['childconn'].send(['ev_wm_factory_mode_success'])
            elif evt == ev_wm_factory_mode_fail:
                errorcode = self.dldtool.get_exit_code()
                self.job['childconn'].send(['ev_wm_factory_mode_fail', errorcode])
            else:
                bes_trace('unknown evt %d' % evt)
        return str_loop

    def dispatch_pip_msg_get_evt_start(self):
        """dispatch_pip_msg_get_evt_start"""
        while True:
            time.sleep(0.05)
            if self.stopped:
                break
            evt = self.dldtool.get_notify_from_cext()
            if ev_wm_port_open_failed <= evt < ev_wm_max:
                ret = self.thread_communicate_with_chip_evt_dispatch(evt)
                if ret == 'leaving':
                    break

        bes_trace('thread_communicate_with_chip_evt_dispatch over')

    def run(self):
        dld_com = self.com
        # dld_com = self.com.decode('utf-8').encode('gbk')

        self.dldtool.handle_buildinfo_to_extend(self.f_file)
        while True:
            time.sleep(0.05)
            rcv = self.job['cconn4dldstart'].recv()
            bes_trace('subprocess dld_thread~~~~~~~~~~~~~~~~~%s~~~~~~~~~~~~~~' % rcv)
            if len(rcv) == 4:
                if rcv[0] == 'MSG_DLD_START':
                    self.argv = []
                    self.argv.append('dldtool.exe')
                    self.argv.append('-C' + dld_com)
                    self.argv.append('-V' + rcv[3])
                    if self.custom_bin_list[0] != '':
                        self.argv.append('-B' + self.custom_bin_list[0])
                    if not rcv[1]:                          # 修复烧录OTA BOOT失败BUG
                        if self.app_switch:
                            # f_file = self.f_file.decode('utf-8').encode('gbk')
                            f_file = self.f_file
                            self.argv.append('-b' + f_file)
                        if self.boot_switch:
                            # fb_file = self.fb_file.decode('utf-8').encode('gbk')
                            fb_file = self.fb_file
                            self.argv.append('-b' + fb_file)
                        if rcv[2] == False and self.app_switch:  # 修复烧录OTA BOOT失败BUG
                            bin_path = os.getcwd() + '\\bin\\' + self.job['factorybin']
                            self.argv.append('-f' + bin_path)
                        self.argv.append('-w' + str(self.burn_field_enable_value))
                    for i in range(1, len(self.custom_bin_list)):
                        if self.custom_bin_list[i] != '':
                            # print('%s' % self.custom_bin_list[i])
                            self.argv.append('-B' + self.custom_bin_list[i])

                    if self.cfg_as_update is False:
                        self.argv.append('-F' + self.connector_switch)
                        self.argv.append('-c' + self.calib_switch)
                        self.argv.append('-P0')
                    else:
                        self.argv.append('-P1')
                    if self.customized_enable == 1:
                        self.argv.append('-K' + self.customized_addr)
                    self.argv.append('-e' + self.eraser_switch)
                    bes_trace(self.argv)

                    arg_var = (c_char_p * (len(self.argv) + 1))()
                    index = 0
                    ''' debug-----以下代码中
                    在Python 3中，默认情况下，所有字符串文字都是unicode。 因此，短语'self.argv'，'-f'，
                    '-d'等都创建了str实例。 为了获取bytes实例，您将需要同时执行以下两项操作：
                    将字节传递到self.argv(username，password，logfile，mount_point和fuse_args中的每个arg
                    将self.argv本身中的所有字符串文字更改为字节：b'fuse'，b'-f'，b'-d'等
                    '''
                    # print(f"argv:\n{self.argv}")
                    for argument in self.argv:
                        argument = bytes(argument, encoding='utf-8')
                        arg_var[index] = argument
                        index += 1

                    arg_ptr = cast(arg_var, POINTER(c_char_p))
                    if self.encrypt_on is True:
                        self.dldtool.dldtool_cfg_set(1)
                        efuseid1 = get_g_efuseID1()
                        efuseid2 = get_g_efuseID2()
                        self.dldtool.set_pin_array(efuseid1, efuseid2)
                    # print(f"arg_ptr{arg_ptr}-------------------")
                    dldret = self.dldtool.dldstart(len(self.argv), arg_ptr)
                    if dldret is 0:
                        bes_trace('dld failure~')
                        break
                    self.dispatch_pip_msg_get_evt_start()
            elif rcv == 'MSG_DLD_END':
                bes_trace('dld_thread recv MSG_DLD_END')
                self.dispatch_pip_msg_terminated()
                self.stopped = True                 # 停止
                break
            else:
                bes_trace('dld_thread rcv ERRORMSG.')

        bes_trace('\ndld_thread over...\n')

    def set_file(self, r_file, f_file, fb_file, app_switch, ota_boot_switch):
        self.r_file = r_file
        self.f_file = f_file
        self.fb_file = fb_file
        self.app_switch = app_switch
        self.boot_switch = ota_boot_switch


class dld_courier(threading.Thread):
    """
        烧录文件加载进程
    """
    encrypt_data = None

    def __init__(self, d, load_dll):
        threading.Thread.__init__(self)
        self.job = d
        self.dldtool = load_dll

    def dispatch_pip_msg_dld_stop(self):
        """dispatch msg MSG_DLD_STOP from main process"""
        self.dldtool.dldstop()
        bes_trace('dldtool.dldstop()')

    def run(self):
        while True:
            time.sleep(0.03)
            bes_trace('dld_courier start..........\n')
            msg_description = self.job['childconn4dldstop'].recv()  # 缓冲区
            if msg_description[0] == 'MSG_DLD_STOP':
                self.dispatch_pip_msg_dld_stop()
                break
            elif msg_description[0] == 'MSG_SYNC_ENCRPYT_DATA':  # 写入的数据
                dld_courier.encrypt_data = copy.deepcopy(msg_description[1])

        bes_trace('\ndld_courier over...\n')


class DldProcess(multiprocessing.Process):
    """
        升级进度线程类
    """
    def __init__(self, job, r_file, f_file, fb_file, app_switch, otaboot_switch,
                 enable_flag, connector_switch, calib_switch, cfg_as_update,
                 burn_field_enable_value, custom_bin_list, encrypt_on, eraser_switch,
                 Customized_enable, Customized_Addr):
        multiprocessing.Process.__init__(self)
        self.job = job
        self.r_file = r_file
        self.f_file = f_file
        self.fb_file = fb_file
        self.app_switch = app_switch
        self.boot_switch = otaboot_switch
        self.sector_update_flag = enable_flag
        self.connector_switch = connector_switch
        self.calib_switch = calib_switch
        self.cfg_as_update = cfg_as_update
        self.burn_field_enable_value = burn_field_enable_value
        self.custom_bin_list = custom_bin_list
        self.encrypt_on = encrypt_on
        self.eraser_switch = eraser_switch
        self.dldtool = None
        self.Customized_enable = Customized_enable
        self.Customized_Addr = Customized_Addr
        return

    def run(self):
        self.dldtool = cdll.LoadLibrary('transferdll.dll')                  # dldtool加载升级封装工具dll
        port_num = self.job['portnum']                                      # 获取当前job的串口号

        dld_courier_thread = dld_courier(self.job, self.dldtool)
        dld_courier_thread.start()
        my_dld_thread = dld_thread(self.job, port_num, self.sector_update_flag, self.connector_switch,
                                   self.calib_switch, self.cfg_as_update, self.burn_field_enable_value,
                                   self.custom_bin_list, self.dldtool, self.encrypt_on, self.eraser_switch,
                                   self.Customized_enable, self.Customized_Addr)
        my_dld_thread.set_file(self.r_file, self.f_file, self.fb_file, self.app_switch, self.boot_switch)
        my_dld_thread.start()
        dld_courier_thread.join()
        my_dld_thread.join()
        bes_trace('\nsubprocess run over...\n')

