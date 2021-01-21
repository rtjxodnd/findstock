# 일별 가격 기준으로 매집봉을 탐색한다.
# 매집봉 기준(아래기준 모두 충족)
# -거래되는 종목이어야 함
# -가격: 당일 거래일의 시-종 차이가 5% 이내 상승
# -거래량: 당일 거래량이 2전거래량의 5배 이상 또는 1전거래량의 3배 이상
# -가격: 당일 종가가 5거래일 평균 이상
from collectData.get_daily_price_info import get_daily_price_info as daily_stock_price_info


# 종목 스크린 main
def search_buying_candle(stc_id):
    # 전달값 저장
    prices_info = daily_stock_price_info(stc_id, 10)[0:10]
    tdy_prices_info = prices_info.iloc[0]
    bf1_prices_info = prices_info.iloc[1]
    bf2_prices_info = prices_info.iloc[2]

    # 거래되는 종목이어야 함: 거래량 없으면 False 리턴
    if tdy_prices_info['거래량'] == 0:
        return {"buying_candle_yn": False, "min_price_of_ten": 0, "tdy_prices_info": tdy_prices_info}

    # 당일의 시-종 차이가 5% 이내 상승. 그외는 False 리턴
    if not 1 <= tdy_prices_info['종가']/tdy_prices_info['시가'] <= 1.05:
        return {"buying_candle_yn": False, "min_price_of_ten": 0, "tdy_prices_info": tdy_prices_info}

    # 당일 거래량이 2전거래량의 5배 이상 또는 1전거래량의 3배 이상. 그외는 False 리턴
    if tdy_prices_info['거래량'] < bf2_prices_info['거래량']*5 and tdy_prices_info['거래량'] < bf1_prices_info['거래량']*3:
        return {"buying_candle_yn": False, "min_price_of_ten": 0, "tdy_prices_info": tdy_prices_info}

    # 당일 종가가 5거래일 평균 이상. 그외는 False 리턴
    if tdy_prices_info['종가'] < prices_info['종가'].head(5).mean():
        return {"buying_candle_yn": False, "min_price_of_ten": 0, "tdy_prices_info": tdy_prices_info}

    # 끝까지 모든 조건 충족시 True, 10거래일간 최저가, 당일가격정보 리턴
    return {"buying_candle_yn": True, "min_price_of_ten": prices_info['종가'].min(), "prices_info": tdy_prices_info}


if __name__ == '__main__':
    print(search_buying_candle('004250'))
