# -*- coding: utf-8 -*-

import requests
from imgyaso import pngquant_bts, \
    adathres_bts, grid_bts, noise_bts, trunc_bts, noisebw_bts
import os
import shutil
import tempfile
import sys
from os import path
import uuid
import numpy as np
import cv2
from BookerWikiTool.util import fname_escape, request_retry, safe_mkdir


def waifu2x_auto(img)：
    fname = path.join(tempfile.gettempdir(), uuid.uuid4().hex + '.png')
    open(fname, 'wb').write(img)
    subp.Popen(
        ['wiki-tool', 'waifu2x-auto', fname], 
        shell=True,
    ).communicate()
    img = open(fname, 'rb').read()
    safe_remove(fname)
    return img

def opti_img(img):
    return noisebw_bts(trunc_bts(waifu2x_auto(img), 4))
        
def safe_remove(name):
    try: os.remove(name)
    except: pass
        
def load_module(fname):
    if not path.isfile(fname) or \
        not fname.endswith('.py'):
        raise FileNotFoundError('外部模块应是 *.py 文件')
    tmpdir = path.join(tempfile.gettempdir(), 'load_module')
    safe_mkdir(tmpdir)
    if tmpdir not in sys.path:
        sys.path.insert(0, tmpdir)
    mod_name = 'x' + uuid.uuid4().hex
    nfname = path.join(tmpdir, mod_name + '.py')
    shutil.copy(fname, nfname)
    mod = __import__(mod_name)
    safe_remove(nfname)
    return mod
    
