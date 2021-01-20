# https://finance.naver.com 으로부터 당일 기준 전종목 정보를 크롤링한다.
import requests
from bs4 import BeautifulSoup
import pandas as pd
import traceback

# 공통변수
FINANCE_URL = "https://finance.naver.com/sise/sise_market_sum.nhn"


# 한페이지의 data 추출
# mkt_tcd: 0코스닥, 1코스피
# page: 웹 페이지 지정
# stockOrder: 해당 페이지 내에서의 순서
def get_today_market_info(mkt_tcd=0, page=1):

    try:
        # 데이터 탐색
        url = FINANCE_URL+"?sosok="+str(mkt_tcd)+"&page="+str(page)
        page_call_result = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        bs_obj = BeautifulSoup(page_call_result.text, 'lxml')
        table_info = bs_obj.find("table", {"class": "type_2"})
        _df = pd.read_html(str(table_info), header=0)[0]
        _df = _df[_df['N'] > 0].reset_index()
        _df = _df.drop(['N', '토론실', '전일비', '액면가', '외국인비율', '등락률', 'PER', 'ROE'], 1)

        # 종목코드 dataframe
        df_stc_id = pd.DataFrame(columns=['종목코드'])

        # 종목코드를 별도 추출
        title_values = table_info.find('tbody').find_all('a', {"class": "tltle"})
        for i, value in enumerate(title_values):
            stc_id = value['href'].split("=")[-1]
            df_stc_id.loc[i] = [stc_id]

        # 추출된 종목코드 dataframe 을 _df에 붙인다.
        _df = pd.concat([df_stc_id, _df], axis=1)

        # 억단위 적용
        _df['시가총액'] = _df['시가총액']*100000000

        # return
        return _df

    except Exception as ex:
        traceback.print_exc(ex)


if __name__ == '__main__':
    print(get_today_market_info(mkt_tcd=0, page=8))
