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

###### 通用版
路由器的使用有点麻烦，每次使用都需要在`config.json`中手动填入wan口的参数
```
netmask：网络掩码
gateway：网关
routerip：路由ip，与gateway相同
bssid：网关mac(以"-"相连，如"ff:ff:ff:ff:ff:ff"应改为"ff-ff-ff-ff-ff-ff")
```
这些参数可以在路由器的web管理界面查看，或者ssh到路由器分别通过`ifconfig`和`arp -a`命令查看。
配置好之后电脑连上wifi，运行kfchinanet即可。

这里提供一个偷懒的方法，先把网线插电脑上，上线再下线，然后把网线插到路由器，电脑连wifi，上线。
**每次使用请务必确保config.json中的相关参数与路由器wan口一致。**

###### openwrt专用版

推荐openwrt或其他支持ssh的路由器使用这个版本[openwrt专用版](https://github.com/sytaxwgl/kfchinanet/tree/openwrt)

## 示例

- 上线

![上线](https://i.loli.net/2018/08/16/5b75209689da9.png)

- 查询在线设备

![在线设备](https://i.loli.net/2018/08/16/5b752096d4a87.png)

- 下线

![下线](https://i.loli.net/2018/08/16/5b752096d4a87.png)

