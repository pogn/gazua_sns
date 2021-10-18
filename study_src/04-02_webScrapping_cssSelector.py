# id값이 없는 경우, CSS 다중설렉터 활용 ->  크롬 개발자도구에서 볼 수 있음
import requests
from bs4 import BeautifulSoup

url = "http://finance.naver.com/item/main.nhn?code=000660"
html = requests.get(url).text

soup = BeautifulSoup(html, "html5lib")
tags = soup.select("#tab_con1 > div:nth-child(3) > table > tbody > tr.strong > td > em") # 크롬에서 제공하는 CSS 다중설렉터를 활용

for tag in tags:
    print(tag.text)