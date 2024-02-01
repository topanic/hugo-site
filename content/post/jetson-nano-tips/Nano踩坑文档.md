+++
title = 'Jetson Nano tips'
date = 2024-01-27T23:58:50+08:00
description = "jetson nano板tensorrt等环境配置"
categories = [
    "Academic Competition"
]
tags = [
    "Jetson Nano",
    "Nvidia",
]

+++




# jetson nano

Jetpack: 4.6.1

- Cuda: 10.2.300
- cuDNN: 8.2.1.32
- TensorRT: 8.2.1.8
- OpenCV: 4.1.1

Python: 3.6.9


# python版本和yolov5

## jetson nano 自带python3.6与yolov5冲突

yolov5 需要满足python版本**大于3.7**，而jetson nano的官方镜像自带版本为 `python3.6.9`，自带的tensorrt也仅仅包含在3.6中，且网上大部分教程都是围绕3.6展开。所以python和yolov5之间在nano中有些冲突。

## 解决方案

以下是我可以想到的两种解决方案：

1. 继续使用 jetson nano 中自带的 python3.6.9。此类方法比较常见，网上大部分教程也是采用次方法。主要思想是在clone yolov5代码时选择早期版本，可以适配python3.6的。*这种解决办法网上教程参差不齐还是需要多辨认一下。*

2. 更换更高版本的python。在这里我使用的是这种方法，理论上来讲可以最高可以换到python3.9，我这里只是为了能跑通yolov5就选择了 `python3.7.12` 。下面部分内容主要讲解此配置方案需要注意的点。


### 包管理工具 

环境管理工具方面选择miniforge3，因为nano架构为aarch64，不同于我们PC的amd64，所以没办法使用anaconda。具体安装方法google搜一下就好，这个简单。

### deepstream的适配性

*如果不知道deepstream是什么东西，那就说明还没有这个需求，可以直接跳过这块，需要的时候再看。*

如果要用到deepstream，其版本要求严格对应cuda版本、jetpack版本等，需要在nvidia官网看好，它也和python版本有严格的对应关系。我在这里使用的是`Deepstream-6.0`，理论与它适配的python版本是3.6.9，我使用python3.7也可以正常运行。

deepstream的安装教程网络上良莠不齐，注意分辨。
这里给出一个比较好的[教程](https://github.com/ultralytics/yolov5/issues/9627)，里面既有对yolov5的安装，也有对deepstream的安装。但还是有刚刚那个python版本问题，其使用的python3.69，所以还是以上**解决方法**中的两个二选一。剩下部分就按照教程走就好。

## 第二种解决办法的后续流程

### tensorrt

tensorrt是一个需要着重说明的点。jetson nano的系统环境其实封装的很好了，其**系统环境中的python3.6.9自带有tensorrt**。可以直接通过 `import tensorrt` 来使用。

但如果要使用高版本的python，就没有tensorrt了，需要自己去编译。

> 为什么不能通过pip安装？ 

还是上面提到的，jetson nano是aarch64架构，pypi官网上无论是tensorrt包还是nvidia-tensorrt包，它的下载栏里面很明显可以看到都是x86架构的，没有办法直接pip下载。

如果留心就会发现tensorrt的python包存在路径：

*/usr/lib/python3.6/dist-packages/tensorrt*

包含以下内容：

- __ init __.py
- tensorrt.so

内容极少，后者就是关键部分，一个编译后的程序函数库文件，我们现在需要做的就围绕它进行。

#### 低版本python：直接链接

如果你创建了python3.6的虚拟环境，发现tensorrt在你的虚拟环境下用不了，就可以简单一点，直接用`ln -s`把这个tensorrt包链接到你的**虚拟环境的site-packages**中。

#### 高版本python：TensorRT Python Bindings

如果是高版本python，例如我这里使用的python3.7.12版本就不能直接链接。这里就要使用到**TensorRT Python Bindings**工具，来编译生成对应版本的**tensorrt.so**。

这里给出两个步骤教程，这两个教程对比着看，就大致学会安装方法。

- [Tensorrt on Jetson with python 3.9](https://forums.developer.nvidia.com/t/tensorrt-on-jetson-with-python-3-9/196131)
- [官方教程](https://github.com/NVIDIA/TensorRT/tree/release/8.2/python)

**注意点：**

- 看好版本，你要使用的python版本，下载好对应的python版本源码。
- TensorRT工具的版本，与我们对应的是**release/8.2**分支。
- cmake版本要高于3.13，系统自带的不满足。

#### 操作过程简述

研究好了上面给的两个教程之后，理论上讲你的目录中需要并列存在以下三个目录：

1. TensorRT：github上克隆的官方工具包
2. pybind11：编译过程中需要使用的子模块
3. python3.x.x：准备好的python include源码，需要加入**pyconfig.h**

第二个我感觉不需要，因为clone了TensorRT之后，使用`git submodule update --init --recursive`就会把pybind11一同clone下来。不过放着也无所谓。

有一个**教程中没有提到的很重要的一个环节**需要做。需要进入：

*TensorRT/parsers/onnx/third_party/onnx/third_party/pybind11*

目录下（如果没有该目录就是没有更新子模块），输入`git checkout -b v2.6`，降低pybind11版本，最新版本有bug。

完成后把参数调整成你需要的之后，执行**build.sh**大概率就是对的，正常情况下会长时间卡在：

``` 
[ 16%] Building CXX object CMakeFiles/tensorrt.dir/src/infer/pyGraph.cpp.o
[ 16%] Building CXX object CMakeFiles/tensorrt.dir/src/infer/pyPlugin.cpp.o
[ 25%] Building CXX object CMakeFiles/tensorrt.dir/src/infer/pyAlgorithmSelector.cpp.o
[ 33%] Building CXX object CMakeFiles/tensorrt.dir/src/infer/pyInt8.cpp.o
[ 41%] Building CXX object CMakeFiles/tensorrt.dir/src/infer/pyFoundationalTypes.cpp.o
[ 50%] Building CXX object CMakeFiles/tensorrt.dir/src/infer/pyCore.cpp.o
[ 58%] Building CXX object CMakeFiles/tensorrt.dir/src/parsers/pyCaffe.cpp.o
[ 66%] Building CXX object CMakeFiles/tensorrt.dir/src/parsers/pyUff.cpp.o
[ 75%] Building CXX object CMakeFiles/tensorrt.dir/src/utils.cpp.o
[ 91%] Building CXX object CMakeFiles/tensorrt.dir/src/parsers/pyOnnx.cpp.o
[ 91%] Building CXX object CMakeFiles/tensorrt.dir/src/pyTensorRT.cpp.o
```
因为这个需要编译一会，如果很快就结束了，大概率是寄了，重新再检查错误吧。

#### 操作过程中的问题合集

> 报错： c++: internal compiler error: Killed (program cc1plus)

编译过程中内存爆了，看[这篇文档](https://aijishu.com/a/1060000000221025)的nano设置部分。

> 报错： ... SetuptoolsDeprecationWarning: setup.py install is deprecated. ... 

python的setuptools版本太高，降版本：`pip install setuptools==58.2.0`

> 报错： "No module named 'tensorrt.tensorrt'" for generated wheel file

遇到这种情况时候，整个流程好像没什么错，但是会发现安装完成之后，tensorrt包里面没有最重要的**tensorrt.so**文件。遇到这种情况就降**pybind11**版本就好。
[issue链接](https://github.com/NVIDIA/TensorRT/issues/2288)

### 完成

完成上述操作后，带有tensorrt的 python3.7就整好了，可以正常用了，另外还需要装一些 pycuda 就很好装了，去pypi官网查看对应python的版本就好，别装错了



# 带有gstream的opencv

原nano板上预装了OpenCV，若直接使用`nvgstcapture`指令可以打开摄像头代表摄像头连接没问题。

现在我们由于更换了python版本，若直接通过pip安装就没办法使用gstream，就会导致打不开CSI摄像头，所以我们需要重新编译适用于python3.7.12的opencv。

## opencv编译过程

具体安装过程可以参照此[博客](https://www.bilibili.com/read/cv17612080/)来完成。

opencv版本我这里选择了4.5.5，此版本目前适用于我们当前环境。

cmake那步具体指令可以根据我下面给出的来适当修改：
```
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D OPENCV_GENERATE_PKGCONFIG=ON -D BUILD_EXAMPLES=OFF -D INSTALL_PYTHON_EXAMPLES=OFF -D INSTALL_C_EXAMPLES=OFF -D PYTHON_EXECUTABLE=$(which python2) -D BUILD_opencv_python2=OFF -D PYTHON3_EXECUTABLE=/home/bad/miniforge3/envs/yolov5/bin/python3.7m -D WITH_GSTREAMER=ON -D PYTHON3_INCLUDE_DIR=/home/bad/miniforge3/envs/yolov5/include/python3.7m -D PYTHON3_PACKAGES_PATH= /home/bad/miniforge3/envs/yolov5/lib/python3.7/site-packages -D PYTHON3_LIBRARY=/home/bad/miniforge3/envs/yolov5/lib/libpython3.7m.so -D PYTHON3_NUMPY_INCLUDE_DIRS=/home/bad/miniforge3/envs/yolov5/lib/python3.7/site-packages/numpy/core/include -D PYTHON_DEFAULT_EXECUTABLE=/home/bad/miniforge3/envs/yolov5/bin/python3.7m ..
```
**最好根据上面给出的cmake指令来进行cmake，不然会make失败**

*建议在make的时候使用 -j4， 这样会快一些，当make到92%的时候使用 -j1，避免卡死*

编译完成后会在根目录生成一个cv目录，此时只需要把cv目录的二进制文件移动到conda中的python3.7环境中即可。完成以上就可以在当前的python环境中使用带gstream的opencv。

# .pt -> .onnx -> .trt

在nano板上使用直接使用pytorch来进行推理的话处理速度会很慢，会导致视频帧率变低。所以在nano板等嵌入式环境中部署深度学习时最好使用tensorrt推理的形式进行，这也是上文讲解tensorrt编译的目的，可以加快一点处理速度。

使用tensorrt推理需要把原pt文件转换为推理引擎文件，通常以 *.engine*或者 *.trt*为主，这两者貌似是一个东西，区别不大，具体有什么区别还需要再研究研究。

从权重文件转换为引擎文件的方式有多种，这里列举主要的三个转换入口：

* TF-TRT，要求是 TensorFlow 模型
* ONNX 模型格式
* 使用 TensorRT API 手动把模型搭起来，然后把参数加载进去

第三种需要使用tensorrt api手动编写网络，比较麻烦，开源项目[Tensorrtx](https://github.com/wang-xinyu/tensorrtx)就使用这种方法来获得.pt文件，但如果网络结构出现问题，那就需要修改此网络结构，极其麻烦。有需要就用一下上述开源项目中的一些模型就好，在以上模型中进行修改。

在本文中使用第二种方法来获得引擎文件，以下是具体流程。

## .pt -> .onnx

这步的转化晚上教程很多，可以参考以下我找的，[U-Net仓库](https://github.com/tsieyy/UNet-dataset)，Main文件夹中的**_04pt2onnx.py**，此代码亲测可用。

## .onnx -> .trt

该步骤麻烦一点，需要源码编译**onnx-tensorrt**，具体步骤可以查看该[博客](https://blog.csdn.net/ll0629/article/details/125082759?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522168205015716800226573759%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=168205015716800226573759&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduend~default-1-125082759-null-null.142^v86^insert_down28,239^v2^insert_chatgpt&utm_term=unet%20tensorrt&spm=1018.2226.3001.4187)。

> 报错： 缺少 <TensorrtRuntimeAPI.h> 文件（我不太确定是不是叫这个名字了，反正是一个差不多的名字）

若出现上述错误，需要在项目文件的CmakeLists.txt文件中添加这个头文件（具体流程百度搜一下，貌似是叫一个 *include_directories* 的指令，记不清了），该头文件的具体位置可以使用：`sudo find / -name TensorrtRuntimeAPI(按实际情况做修改).h` 这条指令来对根目录进行查找，一般情况下就只能找到一个。然后把包含这个头文件的include文件夹放在cmake里边，删掉build文件夹里面的东西重新cmake。cmake没有类似于clean的指令，所以务必要删掉重新来。

**注意**：如果cmake里面有需要对python目录进行修改的就改成我们的conda环境。此步骤记不太清了主要是。

安装完成之后就可以使用下面的指令来进行转换了，如果有报错大概率.onnx文件就有问题：

`onnx2trt best_unet.onnx -o best_unet.trt`

以上步骤做完之后修改编写业务逻辑的代码就可以使用.trt文件来进行推理了。


