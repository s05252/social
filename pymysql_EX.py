import requests
from bs4 import BeautifulSoup
import json
import re
import sys
import time, random
import pandas as pd
import pymysql

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

def get_news(news_url):
    news_detail = []
    print(news_url)
    req = requests.get(news_url, headers=header)
    soup = BeautifulSoup(req.content, 'html.parser')

    # 제목
    title = soup.select('h3#articleTitle')[0].text
    news_detail.append(title)

    # 날짜 
    pdate = soup.select('.t11')[0].get_text()[:11]
    news_detail.append(pdate)

    # 본문
    _text = soup.select('#articleBodyContents')[
        0].get_text().replace('\n', " ")
    text = _text.replace(
        "// flash 오류를 우회하기 위한 함수 추가 function _flash_removeCallback() {}", "")
    news_detail.append(text.strip())

    # 언론사
    pcompany = soup.select('div.article_footer')[
        0].a.get_text().split()[0].strip()
    news_detail.append(pcompany)

    return news_detail

columns = ['날짜', '신문사', '제목', '내용']
df = pd.DataFrame(columns=columns)

query = '코로나'   # url 인코딩 에러는 encoding parse.quote(query)
s_date = "2020.04.01"
e_date = "2020.04.08"
s_from = s_date.replace(".", "")
e_to = e_date.replace(".", "")
page = 1

con = pymysql.connect(host = 'localhost', 
                               user = 'social',
                               passwd = 'socialpassword', 
                               db='socialdb')

cur = con.cursor()

while True:
    time.sleep(random.sample(range(3), 1)[0])
    print(page)

    url = "https://search.naver.com/search.naver?where=news&query=" + query + \
        "&sort=1&field=1&ds=" + s_date + "&de=" + e_date + \
        "&nso=so%3Ar%2Cp%3Afrom" + s_from + "to" + e_to + \
        "%2Ca%3A&start=" + str(page)

    req = requests.get(url, headers=header)
    print(url)
    cont = req.content
    soup = BeautifulSoup(cont, 'html.parser')

    naver_news = soup.find_all("a", {"class": "info"})
    if naver_news == []:
        break

    for a_tag in naver_news:
        try:
            news_url = a_tag.attrs["href"]
            if news_url.startswith("https://news.naver.com"):
                print(news_url)
                news_detail = get_news(news_url)
                print(news_detail)
                df = df.append(pd.DataFrame(
                    [[news_detail[1], news_detail[3], news_detail[0], news_detail[2]]], columns=columns))
                print(df)
                cur.execute('INSERT INTO news_articles VALUES(%s, %s, %s, %s)', (news_detail[1], news_detail[3], news_detail[0], news_detail[2])) 
                con.commit()
        except Exception as e:
            print(e)
            continue
    break
    
    page+=10

    con.close() 
