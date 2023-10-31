爱优腾视频下载器(web端）

## 基本说明

#### 支持内容

1.爱奇艺普通视频以及wvdrm内容

2.腾讯普通视频

3.优酷普通视频，wv加密内容以及自研加密内容

#### 暂不支持

腾讯wv（我网页都播放不了），chacha20（超前买不起）

### 使用说明

只提供win10文件，其余系统自行编译，下载相关依赖

本软件支持解析，不支持破解

1.下载链接中全部文件，放到同一个文件夹

2.第一次运行需要输入三大网站cookie,必须输，**没有会员也要输，除非自己编译**

3.输入链接，然后不报错的话，会生成bat文件或者txt,

bat文件直接运行，

txt需要下载https://www.52pojie.cn/thread-1631141-1-1.html，直接拖进下载器就行

报错的话，根据源码自行修改

## 运行截图

![img](https://s3.ananas.chaoxing.com/sv-w8/doc/c9/08/85/36834fabf123a4ce08f07dfc736d9d50/thumb/1.png)

![img](https://s3.ananas.chaoxing.com/sv-w8/doc/c9/08/85/36834fabf123a4ce08f07dfc736d9d50/thumb/2.png)

![img](https://s3.ananas.chaoxing.com/sv-w8/doc/c9/08/85/36834fabf123a4ce08f07dfc736d9d50/thumb/3.png)

![img](https://s3.ananas.chaoxing.com/sv-w8/doc/c9/08/85/36834fabf123a4ce08f07dfc736d9d50/thumb/4.png)

## 郑重声明

**本软件仅限研究web视频下载技术，所以开源了，软件本身并不重要，其中的部分参数如何逆向才重要**

**比如爱奇艺的vf,虽然只是一个md5，但混淆的相当复杂，以及优酷解密key的jsvmp，还有腾讯的ckey:vmp+wasm以及响应的解密也是一个jsvmp**



## 2023-10-31更新

1.增加腾讯杜比

2.增加爱奇艺4k

3.下载器修复，优酷存在多个map导致下载只有6s，修复爱奇艺wv加密，读取不到init.mp4
