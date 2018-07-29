# -*- coding: utf-8 -*-
# @Time    : 2018/7/29 9:18
# @Author  : sytaxwgl

import re
import os
import json
import time
import random
import psutil
import base64
import hashlib
import requests
from urllib import parse
from proto import user_pb2
from ipaddress import IPv4Address
from pyDes import des, PAD_PKCS5, ECB

with open('config.json', 'r') as f:
    config = json.load(f)
params = config['params']
cpath = config['path']
gtt = 0
path = []
key = ''


def get_net_info(uip):
    '''
    获取网络相关信息
    :param uip:
    :return:
    '''
    values = []
    info = psutil.net_if_addrs()
    for k, v in info.items():
        for item in v:
            if item[0] == 2 and item[1] == uip:
                values.append(item[2])

    tmp = int(IPv4Address(uip)) & int(IPv4Address(values[0]))
    gateway = IPv4Address(tmp)
    gateway = str(IPv4Address(gateway) + 1)
    values.append(gateway)
    values.append(gateway)

    for line in os.popen('arp -a'):

        if line.find(gateway) != -1:
            patt = r'([0-9a-f]{2}[:-]){5}[0-9a-f]{2}'
            bssid = re.search(patt, line)
            bssid = '' if bssid is None else bssid.group(0).replace(':', '-')

    values.append(bssid)
    keys = ['netmask', 'gateway', 'routerip', 'bssid']
    net_info = {k: v for k, v in zip(keys, values)}
    return net_info


def gen_did():
    '''
    生成随机的server_did 和did
    :return:
    '''
    ram_str1 = get_md5(str(time.time()))
    ram_str2 = ram_str1[0:16]
    sdid = ram_str1[0:8] + '-' + ram_str1[8:12] + '-' + ram_str1[12:16] + '-' + ram_str1[16:20] + '-' + ram_str1[20:]
    ram_num = int(random.random() * 10000000)
    imie = '35362607' + str(ram_num) + '0'
    did = imie + '_null_' + ram_str2 + '_null_'
    ram_did = {}
    ram_did.update({'server_did': sdid, 'did': did})
    return ram_did


def initial():
    '''
    初始化config配置信息
    :return:
    '''
    if config['init'] == 0:  # 初始化did,server_did以及帐号和密码
        config['init'] = 1
        ram_did = gen_did()
        params.update(ram_did)
        account = input('请输入帐号：')
        pwd = input('请输入密码：')
        params['mobile'] = account
        params['password'] = pwd

    account = params['mobile'] + ':' + params['password']
    auth = base64.b64encode(account.encode())
    config['header']['Authorization'] = 'Basic %s' % auth.decode()

    net_info = {}
    test_url = 'http://test.f-young.cn'
    try:
        res = requests.get(test_url, allow_redirects=False)
    except requests.exceptions.ConnectionError:
        print("网络连接错误!")
        exit(0)
    if res.status_code == 200:
        return 1

    # 更新网络信息
    elif res.status_code == 302:
        location = parse.urlsplit(res.headers['Location'])
        net_info = parse.parse_qs(location.query)
        for k, v in net_info.items():
            net_info.update({k: v[0]})
        net_info2 = get_net_info(net_info['wlanuserip'])
        net_info.update(net_info2)
        params.update(net_info)
        config['params'].update(params)

    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)
    return 0


def des_descrypt(s, kk):
    """
    DES 解密
    :param s: 加密后的字符串(二进制)
    :return:  解密后的字符串
    """
    secret_key = kk
    k = des(secret_key, ECB, IV=None, pad=None, padmode=PAD_PKCS5)
    de = k.decrypt(s, padmode=PAD_PKCS5)
    de = de.decode()
    return de


def login_chinanet():
    header = config['header']
    url = config['login_url']
    url = url.format(p=params)
    try:
        res = requests.get(url, headers=header)
    except requests.exceptions.ConnectionError:
        print("网络错误！")
        return None
    if res.status_code != 200:
        print(res.text)
        return None
    po = user_pb2.user()
    po.ParseFromString(res.content)
    user_id = po.id
    return user_id


def get_md5(raw_str):
    if type(raw_str) != str:
        return None
    mymd5 = hashlib.md5()
    mymd5.update(raw_str.encode())
    result = mymd5.hexdigest()
    return result


def get_sub_appsign(appsign, tt):
    tt = str(tt)
    nums1 = int(tt[3:7])
    nums2 = int(tt[7:12])
    start = int(nums1 % 668)
    length = int(nums2 / 668)
    if length <= 7:
        length = 8
    if (start + length) >= 668:
        start = 668 - length
    sub_appsign = appsign[start:start + length]
    return sub_appsign


def get_sign(ipath):
    '''
    :param ipath:
    :return:
    '''
    global gtt, key
    appsign = config['appSign64']
    raw_str = config['unsign_str']
    tt = int(time.time() * 1000)
    gtt = tt
    sub_appsign = get_sub_appsign(appsign, tt)
    key = sub_appsign[0:8]
    spath = path[ipath]
    ttype = 7 if ipath == 3 else 4
    if ipath == 4:
        ttype = 11
    raw_str = raw_str.format(p=params, type=ttype, path=spath, time=tt, sub_app_sign=sub_appsign)
    md5_sign = get_md5(raw_str)
    md5_sign = md5_sign.upper()
    return md5_sign


def get_qrcode():
    qr_url = 'https://' + config['host'] + path[0] + '?' + config['qr_params']
    head = config['header']
    md5 = get_sign(0)
    qr_url = qr_url.format(p=params, time=gtt, sign=md5)
    try:
        res = requests.post(qr_url, headers=head)
    except requests.exceptions.ConnectionError:
        print("网络连接错误!")
        return None
    if res.status_code != 200:
        return None
    res_text = des_descrypt(res.content, key)
    res_json = json.loads(res_text)
    hiwf = res_json['response']
    print(hiwf)
    if res_json['status'] != '0':
        hiwf = None
    return hiwf


def get_pwd():
    pwd_url = 'https://' + config['host'] + path[1] + '?' + config['pwd_params']
    md5 = get_sign(1)
    pwd_url = pwd_url.format(p=params, time=gtt, sign=md5)
    res = requests.get(pwd_url, headers=config['header'])
    if res.status_code != 200:
        return None
    res_text = des_descrypt(res.content, key)
    res_json = json.loads(res_text)
    pwd = res_json['response']
    print(pwd)
    if res_json['status'] != '0':
        pwd = None
    return pwd


def online(qrcode, pwd):
    oline_url = 'https://' + config['host'] + path[2] + '?' + config['oline_params']
    md5 = get_sign(2)
    oline_url = oline_url.format(p=params, qrcode=qrcode, pwd=pwd, time=gtt, sign=md5)
    res = requests.post(oline_url, headers=config['header'])
    if res.status_code != 200:
        return None
    res_text = des_descrypt(res.content, key)
    res_json = json.loads(res_text)
    if res_json['status'] == '0':
        print('login successfully!')
    else:
        res_json = None
    return res_json


def list_devices():
    status_url = 'https://' + config['host'] + path[3] + '?' + config['status_params']
    md5 = get_sign(3)
    status_url = status_url.format(p=params, time=gtt, sign=md5)
    try:
        res = requests.get(status_url, headers=config['header'])
    except requests.exceptions.ConnectionError:
        print("网络连接错误!")
        return None
    if res.status_code != 200:
        return None
    res_text = des_descrypt(res.content, key)
    res_json = json.loads(res_text)
    if res_json['status'] != '0':
        print(res_json['response'])
        res_json = None
    return res_json


def kick_off(hiwf):
    kick_url = 'https://' + config['host'] + path[4] + '?' + config['kick_params']
    md5 = get_sign(4)
    kick_url = kick_url.format(p=params, time=gtt, sign=md5, qrcode=hiwf)
    res = requests.delete(kick_url, headers=config['header'])
    if res.status_code != 200:
        return None
    res_text = des_descrypt(res.content, key)
    res_json = json.loads(res_text)
    if res_json['status'] != '0':
        print(res_json['response'])
        res_json = None
    return res_json


if __name__ == '__main__':
    status = initial()
    user_id = login_chinanet()
    if user_id is None:
        exit(0)
    path = [i.format(user_id=user_id) for i in cpath]
    info = '1、上线\n2、在线设备\n3、下线\n0、退出\n\n'
    while True:
        option = input(info)
        if option == '1':
            if status == 1:
                continue
            qrcode = get_qrcode()
            if qrcode is None:
                continue
            pwd = get_pwd()
            result = online(qrcode, pwd)
        elif option == '2':
            dev_list = list_devices()
            if dev_list is not None and dev_list['onlines'] != []:
                for dev in dev_list['onlines']:
                    print('%s, %s' % (dev['device'], dev['time']))
        elif option == '3':
            res = list_devices()
            if res is None or res['onlines'] == []:
                continue
            onlines = res['onlines']
            hiwf = onlines[0]['id']
            res = kick_off(hiwf)
            if res['status'] == '0':
                print('logout successfully!\n')
        else:
            exit(0)
