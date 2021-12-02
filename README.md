# wxChatBot
微信公众号，心理健康相关聊天机器人，国科大2021秋季学期软件工程大作业
## 简易部署
### 1.环境
* 带有公网ip的云服务器,安装好nginx
* 申请好的微信公众号
url是服务器的ip地址
token自定义，相当于密码
![在这里插入图片描述](https://img-blog.csdnimg.cn/a6d3c419e59541a3a222fdc6725e10c9.jpg?x-oss-process=image/watermark,type_d3F5LXplbmhlaQ,shadow_50,text_Q1NETiBAcmV0dXJuIHM=,size_20,color_FFFFFF,t_70,g_se,x_16#pic_center)

### 2.在服务器上配置nginx端口转发

```bash
sudo vim /etc/nginx/sites-available/default
```
在server标签里加入下面的内容（注意url规则与上面微信公众平台匹配）

```
location /weixin {
         proxy_pass http://127.0.0.1:8000;
}

```

### 3.克隆代码运行

```shell
git clone git@github.com:lzbcs/wxChatBot.git

cd wxChatBot
```
在根目录下新建文件夹"gpt2model",把pytorch训练出的语言模型放入文件夹。
```shell
python -m venv venv

pip install -r requirements.txt

sh run.sh
```
### 4.可以进一步使用supervisor管理gunicorn的守护进程
[配置参考](http://supervisord.org/configuration.html)

## 项目地址
https://github.com/lzbcs/wxChatBot
