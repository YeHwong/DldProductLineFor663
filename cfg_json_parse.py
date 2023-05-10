#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time: 2023-02-17 14:23:57
# @File: cfg_json_parse.py
# @Author: YeHwong
# @Email: 598316810@qq.com
# @Version ：1.0.0
import json
import os

cfg_data = {}


def config_json_parse():
    """config_json_parse"""
    global cfg_data
    try:
        cfg_handle = open('user_cfg.json').read()
    except os.error:
        return False
    try:
        cfg_data = json.loads(cfg_handle)
    except os.error:
        return False

    return True


def get_max_burn_num_flag():
    return cfg_data['def_max_burn_num_flag']
