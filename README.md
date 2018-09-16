**这是运行于PC端openwrt路由器专用版**


## 1、源码
安装开发环境和包管理器(以ubuntu为例)
```
sudo apt-get install python3 python3-pip
```
安装第三方模块
```
pip3 install paramiko requests pyDes protobuf
```
运行
```
git clone https://github.com/sytaxwgl/kfchinanet.git
cd kfchinanet
git checkout openwrt
python3 kfchinanet.py
```

## 2、使用方法
在`ssh.json`文件中写入路由器的ssh信息，其中`ifconfig`值可以在路由器中输入`which ifconfig`命令查看
