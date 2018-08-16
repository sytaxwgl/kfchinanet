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
key = ''    # 解密密钥
user_id = 0


def get_net_info(uip):
    '''
    获取网络相关信息
    :param uip: 用户ip
    :return: 键值为'netmask', 'gateway', 'routerip', 'bssid'的字典
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


def generate_did():
    '''
    生成随机的server_did 和did，无实际意义
    :return: did和server_did的字典类型
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
    """
    初始化config配置信息
    :return: 无
    """
    if config['params']['did'] == '':  # 初始化did,server_did以及帐号和密码
        ram_did = generate_did()
        params.update(ram_did)
        account = input('请输入帐号：')
        pwd = input('请输入密码：')
        params['mobile'] = account
        params['password'] = pwd

    account = params['mobile'] + ':' + params['password']
    auth = base64.b64encode(account.encode())
    config['header']['Authorization'] = 'Basic %s' % auth.decode()

    res = test_network()

    # 更新网络信息
    if res.status_code == 302:
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


def test_network():
    test_url = 'http://test.f-young.cn'
    try:
        res = requests.get(test_url, allow_redirects=False)
    except requests.exceptions.ConnectionError:
        print("网络连接错误!")
        exit(1)
    return res


def des_descrypt(s):
    """
    DES 解密
    :param s: 加密后的字符串(二进制)
    :return:  解密后的字符串
    """
    k = des(key, ECB, IV=None, pad=None, padmode=PAD_PKCS5)
    de = k.decrypt(s, padmode=PAD_PKCS5)
    de = de.decode()
    return de


def login_chinanet():
    """
    登录
    :return: 用户id
    """
    header = config['header']
    url = config['login_url']
    url = url.format(p=params)
    try:
        res = requests.get(url, headers=header)
    except requests.exceptions.ConnectionError:
        print("网络错误！")
        exit(1)
    if res.status_code != 200:
        print(res.text)
        exit(0)
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
    ttype = {3: 7, 4: 11}.get(ipath, 4)
    raw_str = raw_str.format(p=params, type=ttype, path=spath, time=tt, sub_app_sign=sub_appsign)
    md5_sign = get_md5(raw_str)
    md5_sign = md5_sign.upper()
    return md5_sign


def do_request(url, ipath, qrcode=None, pwd=None):
    header = config['header']
    md5 = get_sign(ipath)
    url = url.format(p=params, time=gtt, sign=md5, qrcode=qrcode, pwd=pwd)

    if ipath == 0 or ipath == 2:
        rrequest = requests.post
    elif ipath == 4:
        rrequest = requests.delete
    else:
        rrequest = requests.get

    try:
        res = rrequest(url, headers=header)
    except requests.exceptions.ConnectionError:
        print("网络连接错误!")
        exit(1)

    if res.status_code != 200:
        exit(0)
    res_text = des_descrypt(res.content)
    res_json = json.loads(res_text)
    if res_json['status'] != '0':
        print('status: %s, response: %s' % (res_json['status'], res_json['response']))
        exit(0)
    return res_json


def get_qrcode():
    qr_url = 'https://' + config['host'] + path[0] + '?' + config['qr_params']
    res_json = do_request(qr_url, 0)
    hiwf = res_json['response']
    print(hiwf)
    return hiwf


def get_pwd():
    pwd_url = 'https://' + config['host'] + path[1] + '?' + config['pwd_params']
    res_json = do_request(pwd_url, 1)
    pwd = res_json['response']
    print(pwd)
    return pwd


def online(qrcode, pwd):
    online_url = 'https://' + config['host'] + path[2] + '?' + config['oline_params']
    res_json = do_request(online_url, 2, qrcode, pwd)
    print('login successfully!')
    return res_json


def list_devices():
    status_url = 'https://' + config['host'] + path[3] + '?' + config['status_params']
    res_json = do_request(status_url, 3)
    return res_json


def kick_off():
    dev_list = list_devices()['onlines']
    for i in range(0, len(dev_list)):
        print('%d、%s  %s' % (i, dev_list[i]['device'], dev_list[i]['time']))
    option = 0 if len(dev_list) == 1 else input('请选择下线设备：')
    dev = dev_list[option]
    hiwf = dev['id']
    params.update({'wanip': dev['wanIp'], 'brasip': dev['brasIp']})

    kick_url = 'https://' + config['host'] + path[4] + '?' + config['kick_params']
    res_json = do_request(kick_url, 4, qrcode=hiwf)
    print('logout successfully!\n')


if __name__ == '__main__':
    initial()
    user_id = login_chinanet()
    path = [i.format(user_id=user_id) for i in cpath]
    info = '1、上线\n2、在线设备\n3、下线\n0、退出\n\n'

    while True:
        option = input(info)
        if option == '1':
            status_code = test_network().status_code
            if status_code == 302:
                qrcode = get_qrcode()
                pwd = get_pwd()
                online(qrcode, pwd)

        elif option == '2':
            dev_list = list_devices()
            if dev_list['onlines']:
                for dev in dev_list['onlines']:
                    print('%s  %s' % (dev['device'], dev['time']))

        elif option == '3':
            kick_off()

        else:
            exit(0)
