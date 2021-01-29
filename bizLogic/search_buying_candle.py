# 일별 가격 기준으로 매집봉을 탐색한다.
# 매집봉 기준(아래기준 모두 충족)
# -거래되는 종목이어야 함
# -가격: 전거래일의 시-종 차이가 5% 이내 상승
#       당일거래일의 시-종 차이가 3% 이내 상승또는 하락
#       당일 종가가 5거래일 평균의 95% 이상
# -거래: 전거래량이 3전거래량의 5배 이상 또는 2전거래량의 3배 이상
#       당일거래량이 전거래량의 1/4 이하
from collectData.get_daily_price_info import get_daily_price_info as daily_stock_price_info
from commonModule import dy_module


# 종목 스크린 main
def search_buying_candle_1(stc_id, in_dy=None):
    # 일자지정
    if in_dy is None:
        dy_now = dy_module.now_dy()
        dy = dy_now[0:4] + '.' + dy_now[4:6] + '.' + dy_now[6:8]
    else:
        dy = in_dy[0:4] + '.' + in_dy[4:6] + '.' + in_dy[6:8]

    # 전달값 저장
    prices_info = daily_stock_price_info(stc_id, 10)[0:10]
    tdy_prices_info = prices_info.iloc[0]
    bf1_prices_info = prices_info.iloc[1]
    bf2_prices_info = prices_info.iloc[2]
    bf3_prices_info = prices_info.iloc[3]

    # 거래되는 종목이어야 함: 거래량 없으면 False 리턴
    if tdy_prices_info['거래량'] == 0:
        return {"buying_candle_yn": False, "min_price_of_ten": 0, "tdy_prices_info": bf1_prices_info}

    # 전일의 시-종 차이가 5% 이내 상승. 그외는 False 리턴
    if not 1 <= bf1_prices_info['종가']/bf1_prices_info['시가'] <= 1.05:
        return {"buying_candle_yn": False, "min_price_of_ten": 0, "tdy_prices_info": bf1_prices_info}

    # 당일의 시-종 차이가 3% 이내 상승. 또는 하락 그외는 False 리턴
    if tdy_prices_info['종가']/tdy_prices_info['시가'] >= 1.03:
        return {"buying_candle_yn": False, "min_price_of_ten": 0, "tdy_prices_info": bf1_prices_info}

    # 전거래량이 3전거래량의 5배 이상 또는 2전거래량의 3배 이상. 그외는 False 리턴
    if bf1_prices_info['거래량'] < bf3_prices_info['거래량']*5 and bf1_prices_info['거래량'] < bf2_prices_info['거래량']*3:
        return {"buying_candle_yn": False, "min_price_of_ten": 0, "tdy_prices_info": bf1_prices_info}

    # 당일 거래량이 전거래량의 1/4 미만. 그외는 False 리턴
    if tdy_prices_info['거래량']*4 > bf1_prices_info['거래량']:
        return {"buying_candle_yn": False, "min_price_of_ten": 0, "tdy_prices_info": bf1_prices_info}

    # 전일 종가가 5거래일 평균 95% 이상. 그외는 False 리턴
    if bf1_prices_info['종가'] < prices_info['종가'].head(5).mean()*0.95:
        return {"buying_candle_yn": False, "min_price_of_ten": 0, "tdy_prices_info": bf1_prices_info}

    # 끝까지 모든 조건 충족시 True, 10거래일간 최저가, 전일가격정보 리턴
    # 어제의 매집봉을 찾아내므로 전거래일 가격/거래량 정보를 리턴함
    return {"buying_candle_yn": True, "min_price_of_ten": prices_info['저가'].min(), "prices_info": bf1_prices_info}


# 일별 가격 기준으로 특정일의 매집봉을 판별한다.
# 매집봉 기준(아래기준 모두 충족)
# -거래되는 종목이어야 함
# -가격: 당일거래일의 시-종 차이가 5% 이내 상승
#       당일 종가가 5거래일 평균의 95% 이상
# -거래: 당일거래량이 2전거래량의 5배 이상 또는 전거래량의 3배 이상
def search_buying_candle_2(stc_id, in_dy=None):
    # 일자지정
    if in_dy is None:
        dy_now = dy_module.now_dy()
        dy = dy_now[0:4] + '.' + dy_now[4:6] + '.' + dy_now[6:8]
    else:
        dy = in_dy[0:4] + '.' + in_dy[4:6] + '.' + in_dy[6:8]

    # 전달값 저장
    prices_info_all = daily_stock_price_info(stc_id, 30)
    prices_info = prices_info_all[prices_info_all['날짜'] <= dy][0:10]
    tdy_prices_info = prices_info.iloc[0]
    bf1_prices_info = prices_info.iloc[1]
    bf2_prices_info = prices_info.iloc[2]

    # 거래되는 종목이어야 함: 거래량 없으면 False 리턴
    if tdy_prices_info['거래량'] == 0:
        return {"buying_candle_yn": False, "min_price_of_ten": 0, "tdy_prices_info": tdy_prices_info}

    # 당일의 시-종 차이가 10% 이내 상승. 그외는 False 리턴
    if not 1 <= tdy_prices_info['종가']/tdy_prices_info['시가'] <= 1.10:
        return {"buying_candle_yn": False, "min_price_of_ten": 0, "tdy_prices_info": tdy_prices_info}

    # 당일거래량이 2전거래량의 5배 이상 또는 1전거래량의 3배 이상. 그외는 False 리턴
    if tdy_prices_info['거래량'] < bf2_prices_info['거래량']*5 and tdy_prices_info['거래량'] < bf1_prices_info['거래량']*3:
        return {"buying_candle_yn": False, "min_price_of_ten": 0, "tdy_prices_info": tdy_prices_info}

    # 당일 종가가 5거래일 평균 95% 이상. 그외는 False 리턴
    if tdy_prices_info['종가'] < prices_info['종가'].head(5).mean()*0.95:
        return {"buying_candle_yn": False, "min_price_of_ten": 0, "tdy_prices_info": tdy_prices_info}

    # 끝까지 모든 조건 충족시 True, 10거래일간 최저가, 전일가격정보 리턴
    # 당일의 매집봉을 찾아내므로 당일거래일 가격/거래량 정보를 리턴함
    return {"buying_candle_yn": True, "min_price_of_ten": prices_info['저가'].min(), "prices_info": tdy_prices_info}


# 일별 가격 기준으로 특정일의 매집봉을 판별한다.
# 매집봉 기준(아래기준 모두 충족)
# -거래되는 종목이어야 함
# -가격: 당일거래일의 시-종 차이가 5% 이내 상승
#       당일 종가가 5거래일 평균의 95% 이상
# -거래: 당일거래량이 2전거래량의 5배 이상 또는 전거래량의 3배 이상
def search_buying_candle_test(stc_id, in_dy=None):
    # 일자지정
    if in_dy is None:
        dy_now = dy_module.now_dy()
        dy = dy_now[0:4] + '.' + dy_now[4:6] + '.' + dy_now[6:8]
    else:
        dy = in_dy[0:4] + '.' + in_dy[4:6] + '.' + in_dy[6:8]

    # 전달값 저장
    prices_info_all = daily_stock_price_info(stc_id, 30)
    prices_info = prices_info_all[prices_info_all['날짜'] <= dy][0:10]
    tdy_prices_info = prices_info.iloc[0]
    bf1_prices_info = prices_info.iloc[1]
    bf2_prices_info = prices_info.iloc[2]

    # 거래되는 종목이어야 함: 거래량 없으면 False 리턴
    print("거래여부 체크")
    if tdy_prices_info['거래량'] == 0:
        return {"buying_candle_yn": False, "min_price_of_ten": 0, "tdy_prices_info": tdy_prices_info}

    # 당일의 시-종 차이가 10% 이내 상승. 그외는 False 리턴
    print("당일 시가종가 비율체크", tdy_prices_info['종가']/tdy_prices_info['시가'])
    if not 1 <= tdy_prices_info['종가']/tdy_prices_info['시가'] <= 1.10:
        return {"buying_candle_yn": False, "min_price_of_ten": 0, "tdy_prices_info": tdy_prices_info}

    # 당일거래량이 2전거래량의 5배 이상 또는 1전거래량의 3배 이상. 그외는 False 리턴
    print("당일 거래량 비율체크", tdy_prices_info['거래량']/bf2_prices_info['거래량'], tdy_prices_info['거래량']/bf1_prices_info['거래량'])
    if tdy_prices_info['거래량'] < bf2_prices_info['거래량']*5 and tdy_prices_info['거래량'] < bf1_prices_info['거래량']*3:
        return {"buying_candle_yn": False, "min_price_of_ten": 0, "tdy_prices_info": tdy_prices_info}

    # 당일 종가가 5거래일 평균 95% 이상. 그외는 False 리턴
    print("당일 종가 및 5일평균선 체크", tdy_prices_info['종가'], prices_info['종가'].head(5).mean()*0.95)
    if tdy_prices_info['종가'] < prices_info['종가'].head(5).mean()*0.95:
        return {"buying_candle_yn": False, "min_price_of_ten": 0, "tdy_prices_info": tdy_prices_info}

    # 끝까지 모든 조건 충족시 True, 10거래일간 최저가, 전일가격정보 리턴
    # 당일의 매집봉을 찾아내므로 당일거래일 가격/거래량 정보를 리턴함
    print("매집봉 조건 적합")
    return {"buying_candle_yn": True, "min_price_of_ten": prices_info['저가'].min(), "prices_info": tdy_prices_info}


if __name__ == '__main__':
    # print(search_buying_candle('900280'))
    print(search_buying_candle_test('006740', '20201230'))
