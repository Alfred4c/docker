import io
import os
import re

import docker
from flask import Flask, Response, render_template, request
from gzip_stream import GZIPCompressedStream
from werkzeug.test import EnvironBuilder
from werkzeug.wsgi import wrap_file

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
client = docker.DockerClient(base_url="unix://var/run/docker.sock")


class Image:
    def __init__(self, name, tag, size, id):
        self.name = name
        self.tag = tag
        self.size = size
        self.id = id


class GeneratorBytesIO(io.BytesIO):
    def __init__(self, generator):
        super().__init__()
        self.generator = generator

    def read(self, size=-1):
        if size == -1:
            return b"".join(self.generator)
        else:
            data = b""
            while len(data) < size:
                try:
                    chunk = next(self.generator)
                except StopIteration:
                    break
                data += chunk
            return data


@app.route("/")
def test():
    response = os.popen("docker images")
    s = response.read().replace("\n", " ")
    pattern = re.compile(r"\S+")
    list1 = pattern.findall(s)
    images_temp = list1[6:]
    if images_temp[3] == "About":
        del images_temp[3]
    length = len(images_temp)
    images = []
    i = 0
    k = 0
    while i < length:
        image = Image(images_temp[i],
                      images_temp[i + 1], images_temp[i + 6], k)
        images.append(image)
        i = i + 7
        k = k + 1
    return render_template("test.html", list=images)


@app.route("/getlist")
def get_list():
    res = os.popen("docker images")
    return res.read()


@app.route("/save/")
def save():
    image = request.args.get("image", None)
    if not image:
        return "未输入镜像名称"
    tag = request.args.get("tag", None)
    filename = image + "-" + tag + ".tgz"
    res = os.popen("docker save -o {} {}:{}".format(filename, image, tag))
    return res


@app.route("/pull/")
def pull():
    name = request.args.get("image", None)
    if not name:
        return "未输入镜像名称"
    tag = request.args.get("tag", "latest")
    arch = request.args.get("arch", None)
    if arch is None:
        r = os.popen("docker pull {}:{}".format(name, tag))

    else:
        r = os.popen("docker pull --platform {} {}:{}".format(arch, name, tag))
    return r.read()


@app.route("/download/")
def download():
    image = request.args.get("image", None)
    if not image:
        return "未输入镜像名称"
    tag = request.args.get("tag", "latest")
    img = client.images.get("{}:{}".format(image, tag))
    filename = image + "-" + tag + ".tgz"
    builder = EnvironBuilder()
    environ = builder.get_environ()
    iodata = GeneratorBytesIO(img.save())
    compressed = GZIPCompressedStream(iodata, compression_level=7)
    file_send = wrap_file(environ=environ, file=compressed)

    response = Response(file_send, content_type="application/octet-stream")
    response.headers["Content-disposition"] \
        = "attachment; filename=%s" % filename

    return response


if __name__ == "__main__":
    app.run(port=5000, host="0.0.0.0")
