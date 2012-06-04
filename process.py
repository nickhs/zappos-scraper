#!/usr/bin/env python

import pika
import requests
from bs4 import BeautifulSoup
import uuid
import redis
from requests import async

DOMAIN_NAME = "http://www.zappos.com"

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

channel = connection.channel()
channel.queue_declare(queue='main')

print " [x] Waiting for messages. "
value = None

def callback(ch, method, properties, body):
    print " [x] Received url %s" % body
    task(body)
    ch.basic_ack(delivery_tag = method.delivery_tag)

def task(url):
    product = requests.get(url)
    s = BeautifulSoup(product.text)

    global value
    value = s.find('span', 'sku').text.split(':')[-1].strip()

    picurl = DOMAIN_NAME+s.find(id="multiview").get('href')

    pictures = requests.get(picurl)
    x = BeautifulSoup(pictures.text)
    x = x.find(id="no-js-multiview")
    imgs = x.find_all('img')

    linklist = []
    for img in imgs:
        linklist.append(img.get('src'))

    rs = [async.get(link, hooks=dict(response=process_resp)) for link in linklist]
    responses = async.map(rs)
    print "[*] Done "


def process_resp(resp):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)

    image = resp.content
    filename = str(uuid.uuid4()) # key
    # value is the sku of the shoe

    fout = open(filename+'.jpg', 'wb')
    fout.write(image)
    fout.close()

    if value == None:
        r.set(filename, 'FUUUUUCK')
        print "Value is None!!!"

    else:
        print value
        r.set(filename, value)

channel.basic_qos(prefetch_count=2)
channel.basic_consume(callback, queue='main')
channel.start_consuming()
