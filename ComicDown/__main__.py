#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

from urllib.parse import urljoin
import sys
import json
from pyquery import PyQuery as pq
import time
from os import path
import re
from concurrent.futures import ThreadPoolExecutor
from GenEpub import gen_epub
from . import *
from .util import *
from .config import config

img_pool = None

def get_info(html, base):
    root = pq(html)
    if config['remove']:
        root(config['remove']).remove()
    title = root(config['title']).text().strip()
    author = root(config['author']).text().strip()
    el_links = root(config['link'])
    toc = []
    for i in range(len(el_links)):
        url = el_links.eq(i).attr('href')
        if not url: continue
        if base:
            url = urljoin(base, url)
        if not url.startswith('http'):
            continue
        toc.append(url)
    return {'title': fname_escape(title), 'author': fname_escape(author), 'toc': toc}
    
def get_img_src(el_img):
    url = ''
    for prop in config['imgSrc']:
        url = el_img.attr(prop)
        if url: break
    return url
    
def get_chapter(html, base):
    root = pq(html)
    if config['remove']:
        root(config['remove']).remove()
    title = root(config['chTitle']).text().strip()
    el_imgs = root(config['img'])
    imgs = []
    for i in range(len(el_imgs)):
        url = get_img_src(el_imgs.eq(i))
        if not url: continue
        if base:
            url = urljoin(base, url)
        if not url.startswith('http'):
            continue
        imgs.append(url)
    return {'title': fname_escape(title), 'imgs': imgs}
    
def tr_download_img(url, imgs, picname):
    try:
        data = request_retry(
            'GET', url,
            headers=config['headers'],
            retry=config['retry'],
            timeout=config['timeout'],
            proxies=config['proxy'],
        ).content
        data = process_img(data)
        imgs[picname] = data or b''
        time.sleep(config['wait'])
    except Exception as ex:
        print(ex)
        
def process_img(img):
    img = resize_img(img, config['resize'])
    img = opti_img(img, config['optiMode'], config['colors'])
    return img
    
def tr_download_ch(url, info):
    print(f'ch: {url}')
    html = request_retry(
        'GET', url, 
        headers=config['headers'],
        retry=config['retry'],
        timeout=config['timeout'],
        proxies=config['proxy'],
    ).content.decode(config['encoding'])
    ch = get_chapter(html, url)
    if not ch['imgs']:
        print('找不到章节页面')
        return
        
    name = config['fname'] \
        .replace('{title}', info['title']) \
        .replace('{author}', info['author']) \
        .replace('{chapter}', ch['title'])
    ofname = f'{name}.epub'
    if path.exists(ofname):
        if config['overwrite']:
            print('文件已存在')
            return
        else:
            safe_remove(ofname)
    
    imgs = {}
    hdls = []
    for i, img_url in enumerate(ch['imgs']):
        hdl = img_pool.submit(tr_download_img, img_url, imgs, f'{i}.png')
        hdls.append(hdl)
    for h in hdls:
        h.result()
        
    co = '\r\n'.join([
        f"<p><img src='../Images/{i}.png' width='100%' /></p>"
        for i in range(len(imgs))
    ])
    articles = [{'title': name, 'content': co}]
    gen_epub(articles, imgs, None, ofname)
    time.sleep(config['wait'])
    
def tr_download_ch_safe(url, info):
    try: tr_download_ch(url, info)
    except Exception as ex: print(ex)
    
def main():
    global get_info
    global get_chapter
    global img_pool
    
    cfg_fname = sys.argv[1] \
        if len(sys.argv) > 1 \
        else 'config.json'
    if not path.exists(cfg_fname):
        print('please provide config file')
        return
    user_cfg = json.loads(open(cfg_fname, encoding='utf-8').read())
    config.update(user_cfg)
    if config['proxy']:
        proxies = {
            'http': config['proxy'],
            'https': config['proxy'],
        }
        config['proxy'] = proxies
    img_pool = ThreadPoolExecutor(config['imgThreads'])
    if config['external']:
        mod = load_module(config['external'])
        get_toc = getattr(mod, 'get_info', get_info)
        get_article = getattr(mod, 'get_chapter', get_chapter)
    
    html = request_retry(
        'GET', config['url'], 
        headers=config['headers'],
        retry=config['retry'],
        timeout=config['timeout'],
        proxies=config['proxy'],
    ).content.decode(config['encoding'])
    info = get_info(html, config['url'])
    print(info['title'], info['author'])
    
    if len(info['toc']) == 0:
        print('目录获取失败')
        
    ch_pool = ThreadPoolExecutor(config['chThreads'])
    hdls = []
    for url in info['toc']:
        hdl = ch_pool.submit(
            tr_download_ch_safe, url, info)
        hdls.append(hdl)
    for h in hdls: h.result()
    
if __name__ == '__main__': main()