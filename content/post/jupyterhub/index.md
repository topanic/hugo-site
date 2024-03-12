+++
title = 'Jupyterhub'
date = 2024-03-10T23:58:50+08:00
description = "部署TLJH的一些注意点"
tags = [
    "Jupyter",
]
image = "image.png"
+++

# jupyterhub

[jupyterhub](https://jupyter.org/hub)用来提供给多个用户访问notebook的一个工具，
非常适合用在给学生提供jupyter notebook实验环境。

## 安装

jupyterhub提供了两种安装方式：

* Zero to JupyterHub for Kubernetes (ZTJK)
* The Littlest JupyterHub (TLJH)

前者是通过k8s部署在多个服务器上的一种方式，提供更多人访问。
后者是直接部署在一台服务器上的，提供0-100人访问的方式，且该方式不提供docker形式的部署，他要通过systemd以服务的形式完成部署。
本文是通过TLJH方式完成安装。

具体安装流程直接看官方给出的[安装教程](https://tljh.jupyter.org/en/latest/install/custom-server.html)就好，
但是很有可能会启动失败，我使用aliyun服务器按照教程一步步来并不能访问，然后用了Google Cloud服务器也不能成功访问...

完成安装后**访问8000端口并不能访问成功**，官方文档给出的也非常模糊，安装教程中演示的端口号为8000，
配置选项给出的例子又是**8080**端口，所以为了避免访问不到，需要先进行一下配置。

设定配置：`sudo tljh-config set <property-path> <value>`，例如：`sudo tljh-config set http.port 8080`

配置完与网络、代理等相关的配置后，需要重新加载配置：
`sudo tljh-config reload proxy`
，然后重新加载jupyterhub：`sudo tljh-config reload hub`，貌似直接使用`sudl tljh-config reload`也可以还更方便一点。

我这里贴出一个在Aliyun上启动成功的完整的配置:

```yaml
# 命令： root@baipiao:~# tljh-config show
users:
  admin:
  - admin
  - root
https:
  port: 8443
auth:
  DummyAuthenticator:
    password: admin
http:
  port: 8080
user_environment:
  default_app: jupyterlab
```

按照上面的配置应该至少能启动成功。

## 设置https

该部分[教程](https://tljh.jupyter.org/en/latest/howto/admin/https.html)里面说道需要开启https，
开启该项功能需要有域名才行，如果只是单纯的设置`https.enabled = true`，则在重新加载*proxy*的时候会出现错误。

## 用户管理

用户管理这里好像就没什么好说的，官方文档给出的也比较详细，进入管理界面之后添加用户等操作都非常方便。

如果是给学生使用的话，有两个添加用户的方式可能会被用到。

* 添加了用户之后，在用户登陆时候输入密码，之后该用户就直接使用该密码登陆就好了。
* 让用户自行注册账号和密码进行登陆。

以上两个方式设置：

```
sudo tljh-config set auth.type firstuseauthenticator.FirstUseAuthenticator
sudo tljh-config reload
```
```
sudo tljh-config set auth.type nativeauthenticator.NativeAuthenticator
sudo tljh-config reload
```

## 共享文件

[官方教程在这里](https://tljh.jupyter.org/en/latest/howto/content/share-data.html)

**opthon1项**感觉不太用得到，这个可以直接发布一个链接，然后用户点击这个链接就可以直接进入项目。我自己还没有尝试

### 只读文件设置

上述链接网页中的**option2项**，照着那个做就好了。

在这个文件设置过程中发现用户自己创建的文件会在用户的家目录下面，共享的文件会以链接的形式出现在家目录中。

### 用户之间共享

上述链接网页中的**option3项**，还是照着那个做就好了。

我自己还没有尝试过这个


## 查看日志

如果访问不了或者哪里出问题了，那只能看日志才能找到问题，单纯的百度没办法确定问题。

````
sudo journalctl -u jupyterhub

sudo journalctl -u traefik

sudo journalctl -u jupyter-<name-of-user>
````










