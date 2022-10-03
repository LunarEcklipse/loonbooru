import os, sys
from PIL import Image, GifImagePlugin
import shutil

filelist = [f for f in os.listdir("/web/umbreone/rsc/file/full/") if os.path.isfile(os.path.join("/web/umbreone/rsc/file/full/", f))]

size256 = 256, 256
size128 = 128, 128
size64 = 64, 64

for i in filelist: # 256px thumb
    filename = os.path.splitext(i)
    filext = os.path.splitext("/web/umbreone/rsc/file/full/" + i)
    if filext[1] == ".png" or filext[1] == ".jpg":
        shutil.copyfile("/web/umbreone/rsc/file/full/" + i, "/web/umbreone/rsc/file/thumb/256/" + i)
        im = Image.open("/web/umbreone/rsc/file/thumb/256/" + i)
        im.thumbnail(size256, Image.ANTIALIAS)
        im.save("/web/umbreone/rsc/file/thumb/256/" + i)
        im.close()
    elif filext[1] == ".gif":
        im = Image.open("/web/umbreone/rsc/file/full/" + i)
        im.seek(0)
        im.save("/web/umbreone/rsc/file/thumb/256/" + filename[0] + ".png")
        im.close()
        im = Image.open("/web/umbreone/rsc/file/thumb/256/" + filename[0] + ".png")
        im.thumbnail(size256, Image.ANTIALIAS)
        im.save("/web/umbreone/rsc/file/thumb/256/" + filename[0] + ".png")
        im.close()

for i in filelist: # 128px thumb
    filext = os.path.splitext("/web/umbreone/rsc/file/full/" + i)
    filename = os.path.splitext(i)
    if filext[1] == ".png" or filext[1] == ".jpg":
        shutil.copyfile("/web/umbreone/rsc/file/full/" + i, "/web/umbreone/rsc/file/thumb/128/" + i)
        im = Image.open("/web/umbreone/rsc/file/thumb/128/" + i)
        im.thumbnail(size128, Image.ANTIALIAS)
        im.save("/web/umbreone/rsc/file/thumb/128/" + i)
        im.close()
    elif filext[1] == ".gif":
        im = Image.open("/web/umbreone/rsc/file/full/" + i)
        im.seek(0)
        im.save("/web/umbreone/rsc/file/thumb/128/" + filename[0] + ".png")
        im.close()
        im = Image.open("/web/umbreone/rsc/file/thumb/128/" + filename[0] + ".png")
        im.thumbnail(size128, Image.ANTIALIAS)
        im.save("/web/umbreone/rsc/file/thumb/128/" + filename[0] + ".png")
        im.close()

for i in filelist: # 64px thumb
    filename = os.path.splitext(i)
    filext = os.path.splitext("/web/umbreone/rsc/file/full/" + i)
    if filext[1] == ".png" or filext[1] == ".jpg":
        shutil.copyfile("/web/umbreone/rsc/file/full/" + i, "/web/umbreone/rsc/file/thumb/64/" + i)
        im = Image.open("/web/umbreone/rsc/file/thumb/64/" + i)
        im.thumbnail(size64, Image.ANTIALIAS)
        im.save("/web/umbreone/rsc/file/thumb/64/" + i)
        im.close()
    elif filext[1] == ".gif":
        im = Image.open("/web/umbreone/rsc/file/full/" + i)
        im.seek(0)
        im.save("/web/umbreone/rsc/file/thumb/64/" + filename[0] + ".png")
        im.close()
        im = Image.open("/web/umbreone/rsc/file/thumb/64/" + filename[0] + ".png")
        im.thumbnail(size64, Image.ANTIALIAS)
        im.save("/web/umbreone/rsc/file/thumb/64/" + filename[0] + ".png")
        im.close()