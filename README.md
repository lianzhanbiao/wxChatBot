# wxChatBot
微信公众号，心理健康相关聊天机器人，国科大2021秋季学期软件工程大作业
## 简易部署
### 1.环境
* 带有公网ip的云服务器,安装好nginx
* 申请好的微信公众号

### 2.在服务器上配置nginx端口转发

### 3.克隆代码运行

```
git clone git@github.com:lzbcs/wxChatBot.git

cd wxChatBot
```
在根目录下新建文件夹"gpt2model",把pytorch训练出的语言模型放入文件夹。
```
python -m venv venv

pip install -r requirements.txt

sh run.sh
```
### 4.可以进一步使用supervisor管理gunicorn的守护进程
参考：