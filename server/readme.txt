## 运行环境

Python3.7.*

操作系统：Windows

数据库：支持sqlite，mysql，默认数据保存在本地sqlite中。

## 安装步骤
### 一、Python依赖包安装
pip install -r requirements

reuqirements 内容如下:

``` 
alembic==1.7.7
certifi==2021.10.8
cffi==1.15.0
click==8.1.2
colorama==0.4.4
cryptography==36.0.2
Flask==1.0.2
Flask-Cors==3.0.9
Flask-Migrate==2.7.0
Flask-Script==2.0.6
Flask-SQLAlchemy==2.5.1
greenlet==1.1.2
itsdangerous==0.24
Jinja2==2.11.2
Mako==1.2.0
MarkupSafe==1.1.0
pycparser==2.21
PyMySQL==0.9.2
six==1.16.0
SQLAlchemy==1.4.35
Werkzeug==2.1.1
wincertstore==0.2
requests
```

### 二、安装HQChartPy2模块(只支持python3.7)

```
(env3.9) D:\代码\hqchartPy2.Free>python mananger.py runserver
Traceback (most recent call last):
  File "D:\代码\hqchartPy2.Free\mananger.py", line 6, in <module>
    from hqchartPy2 import create_app
  File "D:\代码\hqchartPy2.Free\hqchartPy2\__init__.py", line 6, in <module>
    from hqchartPy2.views import config_blueprint
  File "D:\代码\hqchartPy2.Free\hqchartPy2\views\__init__.py", line 1, in <module>
    from .api import hqchart_api
  File "D:\代码\hqchartPy2.Free\hqchartPy2\views\api.py", line 5, in <module>
    from hqchartPy2.core.hqchartpy2_fast import FastHQChart
  File "D:\代码\hqchartPy2.Free\hqchartPy2\core\hqchartpy2_fast.py", line 7, in <module>
    import HQChartPy2
ModuleNotFoundError: No module named 'HQChartPy2'

```

将HQChartPy2.pdb 和 HQChartPy2.pyd文件复制到python的安装目录,如D:\software\anaconda\envs\env3.9\ 目录中(和python.exe同级)


### 三、初始化话数据库

* python mananger.py db init

* python mananger.py db upgrade 

* python mananger.py db migrate

### 四、运行

**python mananger.py runserver**

运行成功后在浏览器上访问:http://127.0.0.1:8712 就可以访问系统。

默认端口是8712，如果需要更改，修改文件hqchartPy2.Free/hqchartPy2/extention.py中的server_port的值。

如果需要在本机以外访问，需要更改hqchartPy2.Free/hqchartPy2/static/index.js，将其中的http://127.0.0.1:8712的ip地址更改为部署服务器的地址和端口。


### 五、代码目录说明:

```
hqchartPy.Free
├── config.py
├── extention.py
├── hqchartPy2
│   ├── core
│   ├── models
│   ├── static
│   │   ├── images
│   │   └── js
│   │       ├── index.js
│   ├── templates
│   └── views
├── mananger.py
├── requirements
```
* config.py 中，配置了数据sqlite数据库文件的目录，或者mysql数据库的地址的地址。

* extention.py 中定义了一些数据文件交互的地址信息
* hqchartPy2/core 目录中是指标计算平台相关的api逻辑和数据逻辑。
* hqchartPy2/models 数据库表model设计。
* hqchartPy2/static 前端js和图片。
* hqChartPy2/templates 前端页面。
* hqChartPy2/views api路由定义入口。
* requeirements：python依赖包。

### 六、数据同步逻辑说明
初始运行时，需要在界面上设置数据的存放路径。分别是日K线数据，分钟K数据，码表数据，最新一季财务数据，股本数据。

* 分钟K线和日K数据比较大，第一次系统从CDN上拉取数据文件后，存放到指定的目录，后续只做增量更新。本地目录会有一个metainfo.json文件，记录当前本地数据的最新日期，和CDN上的文件列表数据比对，后续只下载本地缺失的数据，然后合并到本地目录中的K线数据中。如果想要重新下载所有数据，只需要更改本地metainfo.json文件的信息。

* 财务数据、股本数据、码表数据比较小，则采取全量更新的方式替换。
* 默认财务数据、股本数据、码表数据会在启动的时候加载到内存中，分钟K线(占内存2.5G左右)和日K数据（占内存2.5G）需要手动加载，服务器内存不够，请谨慎操作。


