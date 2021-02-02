# 필요라이브러리 import
import requests
from bs4 import BeautifulSoup
import pandas as pd
import traceback
FINANCE_URL = "https://comp.fnguide.com/SVO2/ASP/SVD_main.asp?pGB=1&gicode=A{}" \
              "&cID=&MenuYn=Y&ReportGB=&NewMenuID=11&stkGb=&strResearchYN="


# 한건의 data 추출
def get_stc_market_condition(stc_id):
    # 데이터 탐색
    try:
        # 탐색 및 dataframe 화
        url = FINANCE_URL.format(stc_id)
        page_call_result = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        bs_obj = BeautifulSoup(page_call_result.text, 'lxml')
        df = pd.read_html(str(bs_obj.find("table", {"class": "us_table_ty1 table-hb thbg_g h_fix zigbg_no"})))[0]
        df = df.dropna()
        df_data_1 = df[[0, 1]].transpose().reset_index(drop=True)
        df_data_2 = df[[2, 3]].transpose().reset_index(drop=True)
        df_data = pd.concat([df_data_1, df_data_2], axis=1)

        # dataframe 정리
        column = df_data.iloc[0]
        df_data.columns = column
        result = df_data.drop(0)

        # 결과
        return result

    except Exception as ex:
        print("마켓 컨디션 추출중 에러: " + stc_id)
        traceback.print_exc(ex)


if __name__ == '__main__':
    print(get_stc_market_condition('005930'))
