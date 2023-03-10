# docker
1、将代码文件置于docker-download/EN_NFCS/package下

2、在flask-download目录下编写Dockerfile：
FROM python:3.10

ADD ./EF_NFCS/package /code

WORKDIR /code

RUN pip install -i http://pypi.doubanio.com/simple/ --trusted-host pypi.doubanio.com --upgrade -r requirements.txt

CMD ["flask", "run","--host=0.0.0.0"]

3、将docker-download文件夹压缩为docker-download.zip 放在D:\code目录下

4、终端执行命令scp D:\code\docker-download.zip root@10.0.10.141:/root/docker-download3    将docker-download.zip文件复制到10.0.10.141:/root/docker-download3文件夹中

5、cd 到docker-download3文件夹下 

6、执行命令 unzip docker-download.zip解压文件

7、build -t ddocker2 . 创建镜像

8、docker run  -v /var/run/docker.sock:/var/run/docker.sock    -v /root/docker-download3/EF_NFCS/package:/code  -v /usr/bin/docker:/usr/bin/docker  -it -p 5004:5000 
ddocker2       运行

9、访问 10.0.10.141:5004/
