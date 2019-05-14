#!/usr/local/bin/python2.7
# coding:utf-8
from bs4 import BeautifulSoup
import random
import datetime
import codecs
import requests
import os
import time
from pyquery import PyQuery as pq


def get_ip_list(url, headers):
    web_data = requests.get(url, headers=headers)
    soup = BeautifulSoup(web_data.text, 'lxml')
    ips = soup.find_all('tr')
    ip_list = []
    for i in range(1, len(ips)):
        ip_info = ips[i]
        tds = ip_info.find_all('td')
        ip_list.append(tds[1].text + ':' + tds[2].text)
    return ip_list

def get_random_ip(ip_list):
    proxy_list = []
    for ip in ip_list:
        proxy_list.append('http://' + ip)
    proxy_ip = random.choice(proxy_list)
    proxies = {'http': proxy_ip}
    return proxies


#把爬下来的项目上传到自己的GitHub
def git_add_commit_push(date, filename):
    cmd_git_add = 'git add .'
    cmd_git_commit = 'git commit -m "{date}"'.format(date=date)
    cmd_git_push = 'git push -u origin master'

    # os.system函数可以将字符串转化成命令在服务器上运行；其原理是每一条system函数执行时，
    # 其会创建一个子进程在系统上执行命令行，子进程的执行结果无法影响主进程；
    os.system(cmd_git_add)
    os.system(cmd_git_commit)
    os.system(cmd_git_push)


#对每个文件开头写入日期
def createMarkdown(date, filename):
    #open函数用于打开文件，参数为文件名，w表示写文本文件，wb表示编写二进制文件，r表示读文本文件，rb读二进制文件
    with open(filename, 'w') as f:
        f.write("### " + date + "\n")


#根据语言来爬取数据（C++,Python等）
def scrape(language, filename):

    ip_url = 'http://www.xicidaili.com/nn/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17'
    }
    ip_list = get_ip_list(ip_url, headers=headers)
    proxies = get_random_ip(ip_list)

    HEADERS = {
        'User-Agent'	: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
        'Accept'			: 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding'	: 'gzip,deflate,sdch',
        'Accept-Language'	: 'zh-CN,zh;q=0.8'
    }

    url = 'https://github.com/trending/{language}?since=monthly'.format(language=language)
    r = requests.get(url, headers=HEADERS,proxies=proxies)

    assert r.status_code == 200

    # print(r.encoding)

    d = pq(r.content)
    items = d('ol.repo-list li')

    # open()打开后的文件句柄只能写入字符串格式内容，而codecs.open()代开后的文件句柄可以写入unicode格式的内容
    with codecs.open(filename, "a", "utf-8") as f:
        f.write('\n#### {language}\n'.format(language=language))

        for item in items:
            i = pq(item)
            title = i("h3 a").text()
            owner = i("span.prefix").text()
            description = i("p.col-9").text()
            url = i("h3 a").attr("href")
            url = "https://github.com" + url
            # ownerImg = i("p.repo-list-meta a img").attr("src")
            # print(ownerImg)
            f.write(u"* [{title}]({url}):{description}\n".format(title=title, url=url, description=description))
        f.flush()


def job():

    strdate = datetime.datetime.now().strftime('%Y-%m-%d')
    filename = '{date}.md'.format(date=strdate)

    # create markdown file
    createMarkdown(strdate, filename)

    # write markdown
    scrape('python', filename)
    scrape('java', filename)

    # git add commit push
    git_add_commit_push(strdate, filename)


if __name__ == '__main__':
    while True:
        job()

        time.sleep(12 * 60 * 60)