
import pybithumb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl

def get_hpr(ticker):
    try:
        df = pybithumb.get_ohlcv(ticker)
        df = df['2021']

        df['ma5'] = df['close'].rolling(window=5).mean().shift(1) # ma5 = 5일간의 이동평균선
        df['range'] = (df['high'] - df['low']) * 0.5
        df['target'] = df['open'] + df['range'].shift(1)
        df['bull'] = df['open'] > df['ma5']

        fee = 0.0032
        df['ror'] = np.where((df['high'] > df['target']) & df['bull'],
                              df['close'] / df['target'] - fee,
                              1)

        df['hpr'] = df['ror'].cumprod()
        df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100
        return df['hpr'][-2]
    except:
        return 1

def get_ror(k, df):
    df['range'] = (df['high'] - df['low']) * k  # range = 당일 (고가-저가)/2
    df['target'] = df['open'] + df['range'].shift(1) # target  =  당일 시가 +  전일 range(shift(1))가 표시되도록 옮기기

    df['ma5'] = df['close'].rolling(window=5).mean().shift(1) # ma5 = 5일간의 이동평균선
    df['bull'] = df['open'] > df['ma5'] # 시가가 이동평균선보다 높은지 여부

    fee = 0.0032 # 0.002 * 2 + 0.0002  // 0.2%
    # ror열 = ( 종가가 목표가 초과시 매수, 수익률=종가/목표가, 매수실패시 1 )
    df['ror'] = np.where((df['high'] > df['target']) & df['bull'],
                         df['close'] / df['target'] - fee,
                         1)
    df['hpr'] = df['ror'].cumprod() # 기간수익률
    df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100 # MDD = 전고점 대비 몇까지 떨어졌는지


    print("MDD: ", df['dd'].max())
    print("HPR: ", df['hpr'][-2])

    df.to_excel("btc_"+str(int(k))+".xlsx")

    ror = df['ror'].cumprod()[-2] # 전체 수익률 계산

    return ror

def get_score(ticker) : # score =  (시가 - 5일간의 이동평균값)/5일간의 이동평균값
    df = pybithumb.get_ohlcv(ticker)  # 해당 티커의 데이터 전체 추출
    df = df.loc['2021-09', :]  # 2021-09년 데이터만 뽑기
    df['ma5'] = df['close'].rolling(window=5).mean().shift(1)  # ma5 = 5일간의 이동평균값
    df['bull'] = df['open'] > df['ma5']  # bull행  = 시가가 이동평균선보다 높은지 여부
    tk_score = ticker +'score'
    df[tk_score] = (df['open'] - df['ma5']) / df['ma5'] * 100  # **** 시가가 이동평균선보다 얼마나 높은지 ****
    score = df.loc['2021-09', tk_score]
    print(score)
    return score

def get_top5() :
    tickers = pybithumb.get_tickers()  # 모든 거래코인의 티커 가져옴

    top5_ticker = []
    n = 0
    for ticker in tickers:
        score = get_score(ticker)
        if n==3 :
            break

        hprs = []
        for ticker in tickers:
            hpr = get_hpr(ticker)  # 해당 코인의 hpr 계산
            hprs.append((ticker, hpr))
        sorted_hprs = sorted(hprs, key=lambda x: x[1], reverse=True)
        print(sorted_hprs[:5])

        #print(df.head())
        #print(df.tail())
        df.to_excel(ticker+".xlsx")
        break

        #hpr = get_hpr(ticker)  # 해당 코인의 hpr 계산
        #hprs.append((ticker, hpr))

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
    #print(df['range'].dtypes())
    df['target'] = df['open'] + df['range'].shift(1) # target = 당일 시가 + 전일 range(shift(1))가 표시되도록 옮기기

    # 매수조건 2) 시가가 이동평균선보다 높은경우
    df['ma5'] = df['close'].rolling(window=5).mean().shift(1) # ma5 = 5일간의 이동평균선
    df['bull'] = df['open'] > df['ma5'] # 시가가 이동평균선보다 높은지 여부

    # 사졌는지 여부 T/F ( 종가가 목표가 초과시 매수)
    df['buyTF'] = (df['high'] > df['target']) & df['bull']

    # 수익률(ror열) = 샀을경우 수익률 = 종가/목표가, 매수실패시 =1
    df['ror'] = np.where(df['buyTF'], df['close'] / df['target'] - fee, 1)  # ROR
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

    #ror = df['ror'].cumprod()[-2] # 전체 수익률 계산
    #print(ticker)
    #print(df)
    return df


if __name__ == '__main__':
    # X 1) top5 상승장 코인 티커 가져오기
    # X top5_ticker = get_top5()
    '''
    df = pybithumb.get_candlestick('DAS')
    df = df.loc['2020-01-01 00:00:00':'2021-02-01 00:00:00']
    print(df)
    prinerd
    '''


    ###############################
    ### 1) 각 종목별 일일 ror 계산하기

    writer = pd.ExcelWriter('../RESULT/gazua_sns.xlsx', engine='openpyxl') # 필요한 엑셀파일 생성

    # -------------- 변수 --------------
    tickers = ['BTC'] #, 'ETH','ADA', 'BNB','XRP'] # 시가총액 10위 기업 티커 입력
    start_date = '2013-12-27' # 데이터 계산 시작시점 2021
    end_date = '2021-10-01'
    k = 0.5 # 구매여부를 결정하는 변동성 돌파정도
    money = 1 # 투자자산 - 1인경우 비율로만 계산됨
    fee = 0.0042 # 수수료 : 0.002 * 2 + 0.0002  // 0.2%
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

    print(main_df)

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
    plt.figure()
    main_df.plot(kind='line',x='time',y='hpr')
    plt.show()
    print("---------최종---------")
    print("MDD : ", MDD , "%")
    print("HPR : ", HPR , "배")

    # 기간수익률 -> 연복리 계산
    diff = main_df['time'].iloc[-1] - main_df['time'].iloc[0]
    diff = diff.days / 365
    hpr = main_df['hpr'].iloc[-1]
    cagr = ((hpr ** (1 / diff)) - 1) * 100
    print('연복리 : ', cagr)



    '''
    jungin
    df = pybithumb.get_ohlcv(ticker)
    df = df.loc[start_date, :]
    # keys = df['time']
    # keys.to_excel(writer, sheet_name=main) # main tab 추가

    tmp = {}
     # main tab에 write 할 준비
    for ticker in tickers :
        df = pd.read_excel('./RESULT/gazua_sns.xlsx', sheet_name=ticker)
        tmp[ticker] = df['invest_money']

    print(tmp)
    '''




    '''
    dongje

    main_df = pd.DataFrame(columns=['time'])
    for ticker in ticker_list:
        df = pd.read_excel('./coin.xlsx', sheet_name=ticker, engine='openpyxl')
        df_new = df.loc[:, ['time', 'invest']]

        df_new = df_new.rename(columns ={'invest':str(ticker)})

        main_df = pd.merge(main_df, df_new, how='outer', on='time')

    main_df.to_excel('test.xlsx')

    main_df= main_df.fillna(1)
    print(main_df)
    
    main_df['sum'] = (main_df['BTC'] + main_df['ETH'] + main_df['ADA'] + main_df['BNB'] + main_df['XRP']) / 5

    main_df['hpr'] = main_df['sum'].cumprod()
    main_df['dd'] = (main_df['hpr'].cummax() - (main_df['hpr'] / main_df['hpr'].cummax())) * 100
    MDD = main_df['dd'].max()

    main_df.to_excel('result.xlsx')
    print('MDD의 값은 : ' )
    print(MDD)

'''
    # 1-3) 각 5개 코인의 목표가 초과시 매수, 장마감시(24시)매도 했을때 수익률 계산  ror_5 = []

    # 4) ror_5의 합에서 1/5

    # 5) 각 ror의 누적수익률 구하기 (hpr)

    #------------------------#
    '''
    hprs = []
    for ticker in tickers:
        hpr = get_hpr(ticker)  # 해당 코인의 hpr 계산
        hprs.append((ticker, hpr))
    sorted_hprs = sorted(hprs, key=lambda x: x[1], reverse=True)

   

    hprs = []
    for ticker in tickers:
        hpr = get_hpr(ticker) # 해당 코인의 hpr 계산
        hprs.append((ticker, hpr))
    sorted_hprs = sorted(hprs, key=lambda x: x[1], reverse=True)
    print(sorted_hprs[:5])

    high_t5 = sorted_hprs[:5]
    print(type(high_t5[0]['REP']))

    for tk in high_t5 :
        df = pybithumb.get_ohlcv("BTC")
        df = df['2020']

        # ROR, MDD 계산
        for k in np.arange(0.1, 1.0, 0.1):
            print("K: %.1f" % (k))
            ror = get_ror(k, df)
            print("ROR : %f\n" % (ror))
    #------------------------#
    '''
'''
    df = pybithumb.get_ohlcv("BTC")
    df = df['2020']

    # ROR, MDD 계산
    for k in np.arange(0.1, 1.0, 0.1):
        print("K: %.1f"%(k))
        ror = get_ror(k, df)
        print("ROR : %f\n" % (ror))
'''

# df.to_excel("btc.xlsx")
