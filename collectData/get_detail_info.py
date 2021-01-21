from bs4 import BeautifulSoup
import traceback
import requests
import pandas as pd

# 공통변수
FINANCE_URL = "https://finance.naver.com/item/main.nhn?code="


# 한건의 data 추출
def get_detail_info(stc_id):
    try:
        # 데이터 탐색
        url = FINANCE_URL + str(stc_id)
        page_call_result = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        bs_obj = BeautifulSoup(page_call_result.text, 'lxml')

        # 현재가정보
        content_info = bs_obj.find("div", {"id": "content"}).find("p", {"class": "no_today"}).find("em")
        now_price = float(content_info.find_all("span")[0].text.replace(",", ""))

        # 사이드탭 정보
        aside_info = bs_obj.find("div", {"id": "aside"}).find("div", {"class": "aside_invest_info"}).find("div", {"id": "tab_con1"})

        # 시가총액정보(상장주식수)
        df_mrk_cap = pd.read_html(str(aside_info), match='시가총액')[0]
        df_mrk_cap = df_mrk_cap.pivot(columns=0, values=1)['상장주식수'].dropna()
        stc_quantity = float(df_mrk_cap.iloc[0])

        # 투자의견정보(52주 최고/최저가)
        df_opinion = pd.read_html(str(aside_info), match='투자의견')[0]
        df_opinion = df_opinion.pivot(columns=0, values=1)['52주최고l최저'].dropna()
        hi_low = df_opinion.iloc[0].replace(',', '').replace(' ', '').split("l")
        high_52 = float(hi_low[0])
        low_52 = float(hi_low[1])

        # 현재가, 상장주식수, 52주 최고/최저가
        df_price_info = pd.DataFrame({'현재가': [now_price], '상장주식수': [stc_quantity], '52최고가': [high_52], '52최저가': [low_52]})

        # 기업실적분석 테이블 (재무정보)
        df_finance = pd.read_html(str(bs_obj), match='기업실적분석 테이블', header=1)[0]
        df_finance.drop(index=0)
        header = ['매출액', '영업이익', '당기순이익', '영업이익률', '순이익률', '부채비율', '당좌비율', '유보율']
        df_finance = df_finance[df_finance['주요재무정보'].isin(header)]
        df_finance = df_finance.transpose()
        df_finance_year = df_finance.iloc[1:5, :]
        df_finance_year.columns = header
        df_finance_year = df_finance_year.dropna(subset=['매출액']).replace('-', '0')
        df_finance_year = df_finance_year[header].astype('float')
        df_finance_quarter = df_finance.iloc[5:11, :]
        df_finance_quarter.columns = header
        df_finance_quarter = df_finance_quarter.dropna(subset=['매출액']).replace('-', '0')
        df_finance_quarter = df_finance_quarter[header].astype('float')

        return {"가격정보": df_price_info, "년재무정보": df_finance_year, "분기재무정보": df_finance_quarter}
    except Exception as ex:
        print("에러: 상세정보 추출시 에러. 종목코드: {}".format(stc_id))
        traceback.print_exc(ex)


if __name__ == '__main__':
    print(get_detail_info('005930')['가격정보']['현재가'].iloc[0])
