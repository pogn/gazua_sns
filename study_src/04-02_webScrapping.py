# 네이버 파이낸스에서 SK 하이닉스의 배당수익률(PER) 가져오기
import requests
from bs4 import BeautifulSoup

url = "https://finance.naver.com/item/main.nhn?code=000660"
html = requests.get(url).text # request 모듈내의 get 메소드를 호출하여 GET으로 request를 보내고 (텍스트)로 반환
                              # text 메소드는 응답값(텍스트)을 추정되는 인코딩(주로unicod)으로 디코딩하여 넘겨줌
                              # https://docs.python-requests.org/en/master/user/quickstart/

soup = BeautifulSoup(html,"html5lib") # html문서 파싱을 도와주는 beautifulSoup 객체 생성, html5lib라는 모듈을 사용하여 파싱
tags = soup.select("#_per") # select 메소드를 사용하면, CSS Selector를 사용해서 html문서를 파싱함
                            # "#"은 css에서 id임, id = "_per"인 tag를 select하라는소리
                            # 찾은 태그들을 객체리스트로 반환
tag = tags[0] # 한개의 html 문서에는 한개의 id만 있으므로, tags에는 1개의 값만 있음 -> tags[0]
print(tag.text) # tag객체 내의 text메서드를 호출하여 태그 사이에 있는 값만 출력함