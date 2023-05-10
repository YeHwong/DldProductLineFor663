#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2023-02-17 14:25:46
# @File: dld_global.py
# @Author: YeHwong
# @Email: 598316810@qq.com
# @Version ：1.0.0
import array
import binascii
import os
import threading
import time
import uuid
from ctypes import cdll, c_char

from Crypto.Cipher import AES
from Crypto.PublicKey import RSA

g_portUsed = []
g_portNum = []
g_total_port_num = 0
g_f_file_name = ''
g_monitor_threads_mutex = None
G_COMPANY_NAME = 'WT'
G_APP_NAME = 'DLDTOOL'
g_dlddll = None
g_efuseID1 = 255
g_efuseID2 = 255
ev_wm_port_open_failed = 1026
ev_wm_port_open_succeed = 1027
ev_wm_sync_wait = 1028
ev_wm_sync_failed = 1029
ev_wm_sync_succeed = 1030
ev_wm_run_programmer_failed = 1031
ev_wm_run_programmer_succeed = 1032
ev_wm_bin_encrypt_begin = 1033
ev_wm_bin_encrypt_end = 1034
ev_wm_update_sw_ver = 1035
ev_wm_update_product_id = 1036
ev_wm_burn_progress = 1037
ev_wm_burn_magic = 1038
ev_wm_burn_failure = 1039
ev_wm_burn_complt = 1040
ev_wm_burn_efuse_start = 1041
ev_wm_burn_efuse_end = 1042
ev_wm_factory_mode = 1043
ev_wm_block_for_audition = 1044
ev_wm_audition_failure = 1045
ev_wm_burn_audsec_success = 1046
ev_wm_burn_audsec_failure = 1047
ev_wm_chip_power_off = 1048
ev_wm_ready_next_work = 1049
ev_wm_exit_valid = 1050
ev_wm_exit_invalid = 1051
ev_wm_factory_mode_success = 1052
ev_wm_factory_mode_progress = 1053
ev_wm_factory_mode_fail = 1054
ev_wm_factory_calib_value = 1055
ev_wm_exit_user_stop = 1056
ev_wm_read_success = 1057
ev_wm_read_fail = 1058
ev_wm_max = 1059
EXIT_CODE_WAIT_SYNC_ERROR = 14417975


class O(dict):

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


JOBS = [
    O({'ID': 1, 'index': 0, 'portnum': -1, 'stauts': 'stop', 'parentconn': -1, 'childconn': -1,
       'parentconn4dldstop': -1, 'childconn4dldstop': -1,
       'pconn4dldstart': -1, 'cconn4dldstart': -1, 'semaindex': -1, 'monitorthrdindex': -1,
       'factorybin': 'factory1.bin',
       'gen_addr_index': -1, 'btaddrtext': None, 'bleaddrtext': None, 'sntext': None, 'encrypt_path': None,
       'bt_addr_pack': None}),
    O({'ID': 2, 'index': 1, 'portnum': -1, 'stauts': 'stop', 'parentconn': -1, 'childconn': -1,
       'parentconn4dldstop': -1, 'childconn4dldstop': -1,
       'pconn4dldstart': -1, 'cconn4dldstart': -1, 'semaindex': -1, 'monitorthrdindex': -1,
       'factorybin': 'factory2.bin',
       'gen_addr_index': -1, 'btaddrtext': None, 'bleaddrtext': None, 'sntext': None, 'encrypt_path': None,
       'bt_addr_pack': None}),
    O({'ID': 3, 'index': 2, 'portnum': -1, 'stauts': 'stop', 'parentconn': -1, 'childconn': -1,
       'parentconn4dldstop': -1, 'childconn4dldstop': -1,
       'pconn4dldstart': -1, 'cconn4dldstart': -1, 'semaindex': -1, 'monitorthrdindex': -1,
       'factorybin': 'factory3.bin',
       'gen_addr_index': -1, 'btaddrtext': None, 'bleaddrtext': None, 'sntext': None, 'encrypt_path': None,
       'bt_addr_pack': None}),
    O({'ID': 4, 'index': 3, 'portnum': -1, 'stauts': 'stop', 'parentconn': -1, 'childconn': -1,
       'parentconn4dldstop': -1, 'childconn4dldstop': -1,
       'pconn4dldstart': -1, 'cconn4dldstart': -1, 'semaindex': -1, 'monitorthrdindex': -1,
       'factorybin': 'factory4.bin',
       'gen_addr_index': -1, 'btaddrtext': None, 'bleaddrtext': None, 'sntext': None, 'encrypt_path': None,
       'bt_addr_pack': None}),
    O({'ID': 5, 'index': 4, 'portnum': -1, 'stauts': 'stop', 'parentconn': -1, 'childconn': -1,
       'parentconn4dldstop': -1, 'childconn4dldstop': -1,
       'pconn4dldstart': -1, 'cconn4dldstart': -1, 'semaindex': -1, 'monitorthrdindex': -1,
       'factorybin': 'factory5.bin',
       'gen_addr_index': -1, 'btaddrtext': None, 'bleaddrtext': None, 'sntext': None, 'encrypt_path': None,
       'bt_addr_pack': None}),
    O({'ID': 6, 'index': 5, 'portnum': -1, 'stauts': 'stop', 'parentconn': -1, 'childconn': -1,
       'parentconn4dldstop': -1, 'childconn4dldstop': -1,
       'pconn4dldstart': -1, 'cconn4dldstart': -1, 'semaindex': -1, 'monitorthrdindex': -1,
       'factorybin': 'factory6.bin',
       'gen_addr_index': -1, 'btaddrtext': None, 'bleaddrtext': None, 'sntext': None, 'encrypt_path': None,
       'bt_addr_pack': None}),
    O({'ID': 7, 'index': 6, 'portnum': -1, 'stauts': 'stop', 'parentconn': -1, 'childconn': -1,
       'parentconn4dldstop': -1, 'childconn4dldstop': -1,
       'pconn4dldstart': -1, 'cconn4dldstart': -1, 'semaindex': -1, 'monitorthrdindex': -1,
       'factorybin': 'factory7.bin',
       'gen_addr_index': -1, 'btaddrtext': None, 'bleaddrtext': None, 'sntext': None, 'encrypt_path': None,
       'bt_addr_pack': None}),
    O({'ID': 8, 'index': 7, 'portnum': -1, 'stauts': 'stop', 'parentconn': -1, 'childconn': -1,
       'parentconn4dldstop': -1, 'childconn4dldstop': -1,
       'pconn4dldstart': -1, 'cconn4dldstart': -1, 'semaindex': -1, 'monitorthrdindex': -1,
       'factorybin': 'factory8.bin',
       'gen_addr_index': -1, 'btaddrtext': None, 'bleaddrtext': None, 'sntext': None, 'encrypt_path': None,
       'bt_addr_pack': None})]
opt_array = []
bar_array = []
STATE_array = []
TIME_array = []
calib_value_array = []
g_btaddr_display_array = [
    None, None, None, None, None, None, None, None]
g_bleaddr_display_array = [None, None, None, None, None, None, None, None]
g_mainpmonitor_semas = [None, None, None, None, None, None, None, None]
g_monitorthrd_array = [None, None, None, None, None, None, None, None]
g_tool_pri_key = None
g_tool_pub_key = None


def initglobal():
    global g_dlddll
    global g_f_file_name
    global g_portNum
    global g_portUsed
    for i in range(0, 50):
        g_portUsed.append(False)
        g_portNum.append(i)

    g_f_file_name = ''
    bin_exists = os.path.exists('bin')
    if bin_exists is False:
        os.mkdir('bin')
    mainproc_monitor_threads_mutex_init()
    dld_path = os.getcwd() + "\\transferdll.dll"
    g_dlddll = cdll.LoadLibrary(dld_path)      # 调用dll文件


def set_g_efuseID1(efuseid):
    global g_efuseID1
    g_efuseID1 = efuseid


def set_g_efuseID2(efuseid):
    global g_efuseID2
    g_efuseID2 = efuseid


def get_g_efuseID1():
    return g_efuseID1


def get_g_efuseID2():
    return g_efuseID2


def get_dlddll():
    return g_dlddll


def setportUsed(index, value):
    g_portUsed[index] = value


def getportUsed(index):
    return g_portUsed[index]


def setportNum(index, value):
    g_portNum[index] = value


def getportNum(index):
    return g_portNum[index]


def settotalportnum(num):
    global g_total_port_num
    g_total_port_num = num


def gettotalportnum():
    return g_total_port_num


def setffilename(filename):
    global g_f_file_name
    g_f_file_name = filename


def getffilename():
    return g_f_file_name


def getsema(index):
    global g_mainpmonitor_semas
    return g_mainpmonitor_semas[index]


def setsema(index, monitor_sema):
    g_mainpmonitor_semas[index] = monitor_sema


def setmonitorthrd(index, monitorthrd):
    global g_monitorthrd_array
    g_monitorthrd_array[index] = monitorthrd


def getmonitorthrd(index):
    return g_monitorthrd_array[index]


def wt_getpcname():
    return os.environ['COMPUTERNAME']


def mainproc_monitor_threads_mutex_init():
    global g_monitor_threads_mutex
    g_monitor_threads_mutex = threading.Lock()


def get_mainproc_monitor_mutex():
    return g_monitor_threads_mutex


def save_log_to_file(logstring):
    logdir = os.getcwd() + '\\log\\' + wt_getpcname()
    if os.path.exists(logdir):
        pass
    else:
        os.makedirs(logdir)
    threads_mutex = get_mainproc_monitor_mutex()
    threads_mutex.acquire()
    logfile = logdir + '\\' + time.strftime('%Y-%m-%d', time.localtime(time.time())) + '.txt'
    logstring = time.strftime('%H:%M:%S', time.localtime(time.time())) + '   ' + logstring
    file_obj = open(logfile, 'a')
    try:
        file_obj.write(logstring)
    finally:
        file_obj.close()

    threads_mutex.release()


def save_mac_sn_to_file(macstring, sn):
    macsndir = os.getcwd() + '\\macsn\\'
    if os.path.exists(macsndir):
        pass
    else:
        os.makedirs(macsndir)
    threads_mutex = get_mainproc_monitor_mutex()
    threads_mutex.acquire()
    macsnfile_name = macsndir + '\\' + sn + '.txt'
    file_obj = open(macsnfile_name, 'w')
    try:
        file_obj.write(macstring)
    finally:
        file_obj.close()

    threads_mutex.release()


# def get_programmer_bin_path():
#     chiptypestr = ''
#     buf = (c_char * 20)()
#     chiptype_len = get_dlddll().get_chiptype_value(buf)
#     if chiptype_len is not 0:
#         for i in range(chiptype_len):
#             chiptypestr = chiptypestr + str(buf[i])
#
#     programmerbin = os.getcwd() + '\\programmer' + chiptypestr.strip() + '.bin'
#     bes_trace(programmerbin)
#     return programmerbin


def getFileCRC(_path):
    try:
        blocksize = 65536
        f = open(_path, 'rb')
        str = f.read(blocksize)
        crc = 0
        while len(str) != 0:
            crc = binascii.crc32(str, crc)
            str = f.read(blocksize)

        f.close()
    except:
        bes_trace('get file crc error!')
        return 0

    return crc


def bes_trace(*args):
    for arg in args:
        # print(arg)
        pass

    return


def get_tool_rsa_key():
    global g_tool_pri_key
    global g_tool_pub_key
    if g_tool_pri_key is None:
        unpad = lambda s: s[0:-ord(s[-1])]
        aes_secret_key = '12345678901234567890123456789012'
        cipher = AES.new(aes_secret_key)
        key_psw = GlobModule.gen_rsa_password()
        with open('images\\dld_file1.ico', 'rb') as (f):
            encrypted_private_data = f.read()
            f.close()
            decrypted_private_data = unpad(cipher.decrypt(encrypted_private_data))
            try:
                g_tool_pri_key = RSA.importKey(decrypted_private_data, passphrase=key_psw)
            except:
                return [
                    'password_incorrect', [None, None]]

        with open('images\\dld_file2.ico', 'rb') as (f):
            encrypted_pub_data = f.read()
            decrypted_pub_data = unpad(cipher.decrypt(encrypted_pub_data))
            g_tool_pub_key = RSA.importKey(decrypted_pub_data)
            f.close()
    return [
        'succeed', [g_tool_pri_key, g_tool_pub_key]]


class GlobModule:
    dump_pubkey = None

    def __init__(self):
        pass

    @staticmethod
    def egcd(a, b):
        if a == 0:
            return (b, 0, 1)
        g, y, x = GlobModule.egcd(b % a, a)
        return (g, x - b // a * y, y)

    @staticmethod
    def modinv(a, m):
        g, x, _ = GlobModule.egcd(a, m)
        if g != 1:
            raise Exception('No modular inverse')
        return x % m

    @staticmethod
    def dump_public_key(pub_key):
        if GlobModule.dump_pubkey != None:
            return GlobModule.dump_pubkey
        else:
            result = []
            n = pub_key.publickey().n
            bit_n = n.bit_length()
            nwords = bit_n / 32
            B = pow(2, 32)
            N0inv = B - GlobModule.modinv(n, B)
            result.append(N0inv & 255)
            result.append(N0inv >> 8 & 255)
            result.append(N0inv >> 16 & 255)
            result.append(N0inv >> 24 & 255)
            R = pow(2, bit_n)
            RR = pow(R, 2) % n
            for i in range(nwords):
                N = n % B
                result.append(N & 255)
                result.append(N >> 8 & 255)
                result.append(N >> 16 & 255)
                result.append(N >> 24 & 255)
                n = (n / B)

            for i in range(nwords):
                rr = RR % B
                result.append(rr & 255)
                result.append(rr >> 8 & 255)
                result.append(rr >> 16 & 255)
                result.append(rr >> 24 & 255)
                RR = (RR / B)

            GlobModule.dump_pubkey = array.array('B', result)
            return GlobModule.dump_pubkey

    @staticmethod
    def gen_rsa_password():
        userName = userName = os.path.expanduser('~').split('\\')[-1]
        node = uuid.getnode()
        mac = uuid.UUID(int=node).hex[-12:]
        password = userName + '^*&((&Bhj126' + mac + '$^*^(&(*)(_123bagdkhrlwr'
        return password

    @staticmethod
    def convert_char_bin(intger):
        result = []
        result.append(intger & 255)
        int_bin = array.array('B', result)
        return int_bin

    @staticmethod
    def convert_short_bin(intger):
        result = []
        result.append(intger & 255)
        result.append(intger >> 8 & 255)
        int_bin = array.array('B', result)
        return int_bin

    @staticmethod
    def convert_int_bin(intger):
        result = []
        result.append(intger & 255)
        result.append(intger >> 8 & 255)
        result.append(intger >> 16 & 255)
        result.append(intger >> 24 & 255)
        int_bin = array.array('B', result)
        return int_bin

    @staticmethod
    def add_pubkey_signature_to_bin(bin_path, key_addr_int, dump_pubkey, signature):
        efuse1_pos = key_addr_int
        efuse2_pos = efuse1_pos + 1
        key_len_pos = efuse2_pos + 1
        sig_len_pos = key_len_pos + 2
        key_pos = sig_len_pos + 2
        sig_pos = key_pos + 4 + 256 + 256
        pubkey_handle = open(bin_path, 'rb+')
        pubkey_handle.seek(efuse1_pos, 0)
        pubkey_handle.write(GlobModule.convert_char_bin(g_efuseID1))
        pubkey_handle.seek(efuse2_pos, 0)
        pubkey_handle.write(GlobModule.convert_char_bin(g_efuseID2))
        pubkey_handle.seek(key_len_pos, 0)
        pubkey_handle.write(GlobModule.convert_short_bin(len(dump_pubkey)))
        pubkey_handle.seek(sig_len_pos, 0)
        pubkey_handle.write(GlobModule.convert_short_bin(len(signature)))
        pubkey_handle.seek(key_pos, 0)
        pubkey_handle.write(dump_pubkey)
        pubkey_handle.seek(sig_pos, 0)
        pubkey_handle.write(signature)
        pubkey_handle.close()
