
import pybithumb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib as mpl

def get_ror_ji(ticker,start_date,end_date,k,target_vol,money,fee):
    df = pybithumb.get_ohlcv(ticker)
    df = df.loc[start_date:end_date]
    #df = df.loc[start_date, '2021-']

    ######## Data Frame 주요함수 #########
    # cumprod : 누적곱
    # shift
    # rolling(window=5)
    # mean
    # max
    # cummax
    ####################################
    # 매수조건 1) range 값 이상의 변동성 돌파가 있는경우
    df['range'] = (df['high'] - df['low']) * k  # range = 당일 (고가-저가)/2
    df['target'] = df['open'] + df['range'].shift(1) # target = 당일 시가 + 전일 range(shift(1))가 표시되도록 옮기기

    # 매수조건 2) 시가가 이동평균선보다 높은경우
    df['ma5'] = df['close'].rolling(window=5).mean().shift(1) # ma5 = 5일간의 이동평균선
    df['bull'] = df['open'] > df['ma5'] # 시가가 이동평균선보다 높은지 여부

    # 사졌는지 여부 T/F ( 종가가 목표가 초과시 매수)
    df['buyTF'] = (df['high'] > df['target']) & df['bull']

    # 수익률(ror열) = 샀을경우 수익률 = 종가/목표가, 매수실패시 =1
    df['ror'] = np.where(df['buyTF'], df['close'] / df['target'] - fee, 1)  # ROR cf) fee는 금액대비 %이니 ROR에서 계산하면 맞다.
    df['hpr'] = df['ror'].cumprod() # 기간수익률
    df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100 # MDD = 전고점 대비 몇까지 떨어졌는지, 각 일자별로 계산 (마지막 일자를 봐야함)

    # 변동성 조절) 변동성을 조절하기 위해 일일 투자금을 정한다. (money가 1인경우 수익률)
    df['stb'] = ((df['high'] - df['low']) / df['open']) * 100 # 1일 변동성(당일)
    df['stb5'] = df['stb'].rolling(window=5).mean().shift(1) # 5일평균변동성(전일기준)
    df['invest_p'] = target_vol / df['stb5'] * money # 투자금 = 목표변동성/예상변동성(stb5) * 전체자산  => 평균변동성에서 목표변동성만큼 맞추기 위해
    df.loc[(df.invest_p > 1), 'invest_p'] = 1 # 목표변동성 > 실변동성  인경우 전체 투자(1)

    df['not_invest_p'] = (1 - df['invest_p']) * money
    df['invest_after_p'] = df['invest_p'] * df['ror'] # 투자금의 수익률반영된 금액 QQQQ 곱해야하는게 ror인가 hpr인가?
    df['invest_result'] = df['not_invest_p'] + df['invest_after_p'] # 변동성이 반영된 전체 투자 수익
    #df['invest_result'] = df['all_%'].cumprod()  # 변동성이 반영된 전체 투자 수익

    print(ticker)
    print("MDD: ", df['dd'].max(),"%")
    print("HPR: ", df['hpr'][-2],"배")

    str_d = datetime.strptime(start_date, "%Y-%m-%d")
    end_d = datetime.strptime(end_date, "%Y-%m-%d")
    diff = end_d - str_d
    diff = diff.days / 365
    hpr = df['hpr'].iloc[-1]
    cagr = ((hpr ** (1 / diff)) - 1) * 100
    print('연복리 : ', cagr)
    #ror = df['ror'].cumprod()[-2] # 전체 수익률 계산
    #print(ticker)
    #print(df)
    return df


if __name__ == '__main__':
    # X 1) top5 상승장 코인 티커 가져오기
    # X top5_ticker = get_top5()

    ###############################
    ### 1) 각 종목별 일일 ror 계산하기

    writer = pd.ExcelWriter('./RESULT/gazua_sns.xlsx', engine='openpyxl') # 필요한 엑셀파일 생성

    # -------------- 변수 --------------
    tickers = ['BTC','ETH'] #, 'ETH','ADA', 'BNB','XRP'] # 시가총액 10위 기업 티커 입력
    start_date = '2013-12-27' # 데이터 계산 시작시점 2021
    end_date = '2021-10-12'
    k = 0.5 # 구매여부를 결정하는 변동성 돌파정도
    money = 1 # 투자자산 - 1인경우 비율로만 계산됨
    fee = 0.0032 # 수수료 : 0.002 * 2 + 0.0002  // 0.2%
    target_vol = 2 # 목표 변동성 (% 임)
    # ----------------------------------
    for ticker in tickers:
        df = get_ror_ji(ticker, start_date, end_date, k, target_vol, money, fee)
        df.to_excel(writer, sheet_name=ticker)
        writer.save()

    ###############################
    ### 2) 종목별 투자 수익률 가져오기

    main_df = pd.DataFrame(columns=['time']) # time열 추가

    for ticker in tickers:
        df = pd.read_excel('./RESULT/gazua_sns.xlsx', sheet_name=ticker, engine='openpyxl')
        df_new = df.loc[:, ['time', 'invest_result']]
        df_new = df_new.rename(columns={'invest_result': str(ticker)})
        main_df = pd.merge(main_df, df_new, how='outer', on='time')

    main_df = main_df.fillna(1)
    main_df.to_excel('./RESULT/tmp.xlsx')

    x = 0
    for ticker in tickers:
        if x == 0 :
            main_df['sum'] = main_df[ticker]
            x = x + 1
        else :
            main_df['sum'] = main_df['sum'] + main_df[ticker]

    # 5 종목 MDD 계산
    main_df['ror'] = main_df['sum'] / len(tickers)
    main_df['hpr'] = main_df['ror'].cumprod() # 누적수익률
    main_df['dd'] = (main_df['ror'].cummax() - (main_df['ror'] / main_df['ror'].cummax())) * 100


    MDD = main_df['dd'].max()
    HPR = main_df['hpr'].iloc[-1]
    main_df.to_excel('./RESULT/result.xlsx')


    print("---------최종---------")
    print("MDD : ", MDD , "%")
    print("HPR : ", HPR , "배")

    # 기간수익률 -> 연복리 계산
    diff = main_df['time'].iloc[-1] - main_df['time'].iloc[0]
    diff = diff.days / 365
    hpr = main_df['hpr'].iloc[-1]
    cagr = ((hpr ** (1 / diff)) - 1) * 100
    print('연복리 : ', cagr)

    # --------- graph ---------
    ys = ['open'] #, 'ma5', 'target']
    df.plot(kind='line', x='time', y=ys)
    plt.show()
