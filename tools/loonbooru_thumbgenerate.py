import os, sys
from PIL import Image, GifImagePlugin
import shutil

filelistfull = [f for f in os.listdir("/home/lunar/projects/webserv/loonbooru/rsc/file/full") if os.path.isfile(os.path.join("/home/lunar/projects/webserv/loonbooru/rsc/file/full", f))]
filelistthumb64 = [f for f in os.listdir("/home/lunar/projects/webserv/loonbooru/rsc/file/thumb/64") if os.path.isfile(os.path.join("/home/lunar/projects/webserv/loonbooru/rsc/file/thumb/64", f))]
filelistthumb128 = [f for f in os.listdir("/home/lunar/projects/webserv/loonbooru/rsc/file/thumb/128") if os.path.isfile(os.path.join("/home/lunar/projects/webserv/loonbooru/rsc/file/thumb/128", f))]
filelistthumb256 = [f for f in os.listdir("/home/lunar/projects/webserv/loonbooru/rsc/file/thumb/256") if os.path.isfile(os.path.join("/home/lunar/projects/webserv/loonbooru/rsc/file/thumb/256", f))]

size256 = 256, 256
size128 = 128, 128
size64 = 64, 64

for i in filelistfull: # 256px thumb
    for j in filelistthumb256:
        if j == i:
            continue
    filename = os.path.splitext(i)
    filext = os.path.splitext("/home/lunar/projects/webserv/loonbooru/rsc/file/full/" + i)
    if filext[1] == ".png" or filext[1] == ".jpg":
        shutil.copyfile("/home/lunar/projects/webserv/loonbooru/rsc/file/full/" + i, "/home/lunar/projects/webserv/loonbooru/rsc/file/thumb/256/" + i)
        im = Image.open("/home/lunar/projects/webserv/loonbooru/rsc/file/thumb/256/" + i)
        im.thumbnail(size256, Image.ANTIALIAS)
        im.save("/home/lunar/projects/webserv/loonbooru/rsc/file/thumb/256/" + i)
        im.close()
    elif filext[1] == ".gif":
        im = Image.open("/home/lunar/projects/webserv/loonbooru/rsc/file/full/" + i)
        im.seek(0)
        im.save("/home/lunar/projects/webserv/loonbooru/rsc/file/thumb/256/" + filename[0] + ".png")
        im.close()
        im = Image.open("/home/lunar/projects/webserv/loonbooru/rsc/file/thumb/256/" + filename[0] + ".png")
        im.thumbnail(size256, Image.ANTIALIAS)
        im.save("/home/lunar/projects/webserv/loonbooru/rsc/file/thumb/256/" + filename[0] + ".png")
        im.close()

for i in filelistfull: # 128px thumb
    for j in filelistthumb128:
        if j == i:
            continue
    filename = os.path.splitext(i)
    filext = os.path.splitext("/home/lunar/projects/webserv/loonbooru/rsc/file/full/" + i)
    if filext[1] == ".png" or filext[1] == ".jpg":
        shutil.copyfile("/home/lunar/projects/webserv/loonbooru/rsc/file/full/" + i, "/home/lunar/projects/webserv/loonbooru/rsc/file/thumb/128/" + i)
        im = Image.open("/home/lunar/projects/webserv/loonbooru/rsc/file/thumb/128/" + i)
        im.thumbnail(size128, Image.ANTIALIAS)
        im.save("/home/lunar/projects/webserv/loonbooru/rsc/file/thumb/128/" + i)
        im.close()
    elif filext[1] == ".gif":
        im = Image.open("/home/lunar/projects/webserv/loonbooru/rsc/file/full/" + i)
        im.seek(0)
        im.save("/home/lunar/projects/webserv/loonbooru/rsc/file/thumb/128/" + filename[0] + ".png")
        im.close()
        im = Image.open("/home/lunar/projects/webserv/loonbooru/rsc/file/thumb/128/" + filename[0] + ".png")
        im.thumbnail(size128, Image.ANTIALIAS)
        im.save("/home/lunar/projects/webserv/loonbooru/rsc/file/thumb/128/" + filename[0] + ".png")
        im.close()

for i in filelistfull: # 64px thumb
    for j in filelistthumb64:
        if j == i:
            continue
    filename = os.path.splitext(i)
    filext = os.path.splitext("/home/lunar/projects/webserv/loonbooru/rsc/file/full/" + i)
    if filext[1] == ".png" or filext[1] == ".jpg":
        shutil.copyfile("/home/lunar/projects/webserv/loonbooru/rsc/file/full/" + i, "/home/lunar/projects/webserv/loonbooru/rsc/file/thumb/64/" + i)
        im = Image.open("/home/lunar/projects/webserv/loonbooru/rsc/file/thumb/64/" + i)
        im.thumbnail(size64, Image.ANTIALIAS)
        im.save("/home/lunar/projects/webserv/loonbooru/rsc/file/thumb/64/" + i)
        im.close()
    elif filext[1] == ".gif":
        im = Image.open("/home/lunar/projects/webserv/loonbooru/rsc/file/full/" + i)
        im.seek(0)
        im.save("/home/lunar/projects/webserv/loonbooru/rsc/file/thumb/64/" + filename[0] + ".png")
        im.close()
        im = Image.open("/home/lunar/projects/webserv/loonbooru/rsc/file/thumb/64/" + filename[0] + ".png")
        im.thumbnail(size64, Image.ANTIALIAS)
        im.save("/home/lunar/projects/webserv/loonbooru/rsc/file/thumb/64/" + filename[0] + ".png")
        im.close()