## 简介
kfchinanet是由python3编写的电信校园网认证工具。接口来自掌上大学app，你可以使用这个工具简化上网步骤。


## 使用方法：
#### 1、可执行文件

下载对应平台的可执行文件，按提示使用即可。

#### 2、源码
kfchinanet 使用的开发环境为python3.5，并且调用了一些第三方模块。你可以使用pip命令安装这些模块。
```
pip install psutil requests pyDes protobuf
```
如果你的系统python2和python3共存，请使用pip3代替pip。安装好相关模块之后直接运行kfchinanet.py文件即可。


## 示例

- 上线

![上线](https://i.loli.net/2018/08/16/5b75209689da9.png)

- 查询在线设备

![在线设备](https://i.loli.net/2018/08/16/5b752096d4a87.png)

- 下线

![下线](https://i.loli.net/2018/08/16/5b752096d4a87.png)

## 支持平台
win10和ubuntu 18.04可以正常使用，mac未测试，不支持使用路由器。