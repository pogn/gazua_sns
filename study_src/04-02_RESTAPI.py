# ch04/04_09.py
import requests
import datetime

r = requests.get("https://api.korbit.co.kr/v1/ticker/detailed?currency_pair=btc_krw") # response 객체(r)는 json데이터 타입으로 구성
bitcoin = r.json() # r 객체내의 json 메소드를 통해 JSON데이터-> python딕셔너리로 변환

timestamp = bitcoin['timestamp']
date = datetime.datetime.fromtimestamp(timestamp / 1000) # 출력 및 활용에 용의하게 하기위해, fromtimestamp 함수를 통해
                                                         # timestamp값을 datetime 객체로 변환
print(date)