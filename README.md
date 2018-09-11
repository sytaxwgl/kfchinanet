## 简介
kfchinanet是由python3编写的电信校园网认证工具。接口来自掌上大学app，你可以使用这个工具简化上网步骤。


## 使用方法：

#### 1、可执行文件

[release页面](https://github.com/sytaxwgl/kfchinanet/releases)下载对应平台的可执行文件，按提示使用即可。

#### 2、源码
安装开发环境和包管理器(以ubuntu为例)
```
sudo apt-get install python3 python3-pip
```
安装第三方模块
```
pip3 install psutil requests pyDes protobuf
```
运行
```
git clone https://github.com/sytaxwgl/kfchinanet.git
cd kfchinanet
python3 kfchinanet.py
```

#### 3、路由器
敬请期待......

## 示例

- 上线

![上线](https://i.loli.net/2018/08/16/5b75209689da9.png)

- 查询在线设备

![在线设备](https://i.loli.net/2018/08/16/5b752096d4a87.png)

- 下线

![下线](https://i.loli.net/2018/08/16/5b752096d4a87.png)

## 支持平台
win10和ubuntu 18.04可以正常使用，mac未测试，不支持使用路由器。

## 开发&参与
本周内(2018/9/11)打算增加对路由器的支持， 方便参与测试或者对开发过程感兴趣的同学可以在Telegram私聊我[@TTups](https://t.me/TTups)。
