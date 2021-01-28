# 일별 가격 기준으로 매집봉을 탐색한다.
# 매집봉 기준(아래기준 모두 충족)
# -거래되는 종목이어야 함
# -가격: 전거래일의 시-종 차이가 5% 이내 상승
#       당일거래일의 시-종 차이가 3% 이내 상승또는 하락
#       당일 종가가 5거래일 평균의 95% 이상
# -거래: 전거래량이 3전거래량의 5배 이상 또는 2전거래량의 3배 이상
#       당일거래량이 전거래량의 1/4 이하
from collectData.get_daily_price_info import get_daily_price_info as daily_stock_price_info


# 종목 스크린 main
def search_buying_candle(stc_id):
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


if __name__ == '__main__':
    print(search_buying_candle('900280'))
