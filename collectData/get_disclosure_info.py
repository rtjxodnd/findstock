# https://finance.naver.com 으로부터 주어진 일동안의 일별 시고저종 및 거래량정보를 크롤링한다.

# 필요라이브러리 import
import requests
from bs4 import BeautifulSoup
import pandas as pd
import math
import traceback

# 공통변수
FINANCE_URL = "https://finance.naver.com/item/news_notice.nhn?code={}&page={}"


# 해당 종목의 마지막 page 확인
def get_last_page_of_disclosure(stc_id):
    try:
        url = FINANCE_URL.format(stc_id, '1')
        page_call_result = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        bs_obj = BeautifulSoup(page_call_result.content, "html.parser")
        td_pg_rr = bs_obj.find("td", {"class": "pgRR"})

        # 마지막 페이지가 가리키는 위치 확인
        # 마지막 페이지 링크버튼 없다면 해당 종목은 1개의 페이지만 존재한다.
        if td_pg_rr is None:
            last_page = 1
        else:
            href = td_pg_rr.find("a")["href"]
            last_page = int(href.split("=")[2])

        return last_page

    except Exception as ex:
        print("공지정보 마지막 페이지번호 추출 중 에러: " + stc_id)
        traceback.print_exc(ex)


# 한개 page 처리
def find_disclosure_info_of_one_page(stc_id, page=1):
    try:
        # 데이터 탐색
        url = FINANCE_URL.format(stc_id, page)
        page_call_result = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        bs_obj = BeautifulSoup(page_call_result.text, 'lxml')
        _df = pd.read_html(str(bs_obj.find("table")), header=0)[0]
        _df = _df.dropna()

        # return
        return _df
    except Exception as ex:
        print("에러: " + stc_id + " [" + str(page) + "page]")
        traceback.print_exc(ex)


# Main 처리: 마지막페이지를 구하고 첫 페이지부터 마지막페이지까지 크롤링
def get_disclosure_info(stc_id, goal_day):
    # 결과 data frame 초기화
    result_value = None

    # 마지막 페이지
    last_page = get_last_page_of_disclosure(stc_id)

    for page in range(1, last_page+1):
        # 한페이지 추출
        df = find_disclosure_info_of_one_page(stc_id, page)

        # 추출정보중 가장 오랜된 날짜 확인
        oldest_day = df['날짜'].iloc[-1].replace('.', '')

        # data 취합
        result_value = pd.concat([result_value, df], ignore_index=True)

        # 추출정보중 가장 과거 날짜가 목표한 날짜 보다 과거 날짜이면 그만 추출한다.
        if oldest_day <= goal_day:
            break

    return result_value


if __name__ == "__main__":
    # print(get_last_page_of_disclosure('352820'))
    print(get_disclosure_info('005930', '20190901'))
