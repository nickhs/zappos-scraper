from bs4 import BeautifulSoup
import requests
import gevent ## may not be needed
import os
from requests import async

DOMAIN_NAME = "http://www.zappos.com/"

def main():
    start_page = 1
    end_page = 4
    counter = start_page

    for page in xrange(start_page, end_page):
        import pdb; pdb.set_trace()
        page = get_page(counter)
        img_list = get_img_list(page)
        save_images(img_list)
        counter = counter+1
        print "Finished, starting "+str(counter)


def main2():
    start_page = 1
    end_page = 4
    counter = start_page

    for page in xrange(start_page, end_page):
        page = get_page(counter)
        links = extract_product_pages(page)
        process_product_pages(links)



def get_page(page_num):
    page_num = str(page_num)
    url = "http://www.zappos.com/shoes~3W?p="+page_num+"&s=recentSalesStyle/desc/"
    r = requests.get(url)
    
    if r.status_code is not 200:
        print r.status_code+": Failed to get: "+url
        return None

    print "Successful"
    return r.text


def get_img_list(text):
    s = BeautifulSoup(text)

    images = s.find_all("img", "productImg")

    if len(images) == 100:
        return images

    elif len(images) is not 0:
        print "Got "+len(x)+" going anyway"
        return images

    elif len(images) == 0:
        print "Failed! Got nothing"
        return None

    else:
        print "What the fuck...?"
        import pdb; pdb.set_trace()
        return None


def save_images(img_list):
    threads = [gevent.spawn(make_img, i, img_list[i].get("src"), img_list[i].get("alt")) for i in xrange(len(img_list))]
    gevent.joinall(threads)


def make_img(pid, url, name):
    resp = requests.get(url)

    if resp.status_code is 200:
        fout = open(name, "wb")
        fout.write(resp.content)
        fout.close()
        print "Completed ["+str(pid)+"] getting "+name

    else:
        print "Failed! Bad Status Code"

def extract_product_pages(page):
    s = BeautifulSoup(page)
    search_results = s.find(id="searchResults")
    links = search_results.find_all('a')
    
    ## This a list of links to the individual product pages
    return links


def process_product_pages(links):
    for link in links:
        url = DOMAIN_NAME+link.get('href')
        name = link.get('href').strip('/')
        linklist = extract_product_picutres(url)

        path = './'+name
        if os.path.exists(path):
            print "WTF"
            return None

        os.makedirs(path)
        os.chdir(path)

        rs = [async.get(link, hooks=dict(response=process_resp)) for link in linklist]
        responses = async.map(rs)

## FIXME


def process_resp(resp):
    image = resp.content

    fout = open(resp.url, 'wb')
    fout.write(image)
    fout.close()
    print "Saved image!"


def extract_product_pictures_links(url):
    product = requests.get(url)
    s = BeautifulSoup(product.text)

    picurl = DOMAIN_NAME+s.find(id="multiview").get('href')

    pictures = requests.get(picurl)
    x = BeautifulSoup(pictures.text)
    x = x.find(id="no-js-multiview")
    imgs = x.find_all('img')

    linklist = []
    for img in imgs:
        linklist.append(img.get('src'))

    return linklist




if "__main__" == __name__:
    main2()
