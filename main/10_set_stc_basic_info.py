# 당일 기준 전종목 정보를 가져와서 종목 기본정보 및 일별 정보를 저장한다.
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
import requests
import traceback
from bs4 import BeautifulSoup
from commonModule import db_module, dy_module
from collectData.get_today_market_info import get_today_market_info
from commonModule.telegram_module import send_message_to_friends

# 공통변수
FINANCE_URL = "https://finance.naver.com/sise/sise_market_sum.nhn"


# 기존 data delete
def stock_values_delete():

    try:
        db_class = db_module.Database()
        sql = "DELETE from findstock.sc_stc_basic"
        db_class.execute(sql)
        db_class.commit()

    except Exception as ex:
        print("에러: 기존 데이터 삭제시 에러. (findstock.sc_stc_basic)")
        traceback.print_exc(ex)

    return


# 마지막 page 확인
def get_last_page_of_stock(mkt_tcd):
    try:
        url = FINANCE_URL+"?sosok="+str(mkt_tcd)
        page_call_result = requests.get(url)
        bs_obj = BeautifulSoup(page_call_result.content, "html.parser")
        td_pg_rr = bs_obj.find("td", {"class": "pgRR"})

        # 마지막 페이지가 가리키는 위치 확인
        href = td_pg_rr.find("a")["href"]
        lp = int(href.split("=")[2])

    except Exception as ex:
        print("에러: 마지막페이지 획득시 에러. 마켓구분:"+mkt_tcd)
        traceback.print_exc(ex)

    return lp


# 마켓(코스피 or 코스닥)별 종목기본정보 저장
def set_stc_basic_market_info(mkt_tcd=0):
    # 마지막 page 확인
    last_page = get_last_page_of_stock(mkt_tcd)

    # 시장코드설정
    if mkt_tcd == 0:
        mkt_nm = 'KRX'
    elif mkt_tcd == 1:
        mkt_nm = 'KOSDAQ'
    else:
        mkt_nm = None

    # db 모듈
    db_class = db_module.Database()

    # 각 page 반복
    for page in range(1, last_page+1):
        # 각 행 반복
        df_stc_values = get_today_market_info(mkt_tcd, page)
        for i, row in df_stc_values.iterrows():
            # 주식구분 설정(보통주, 우선주, 스팩주)
            stc_tcd = 'common'
            if row['종목명'].count('스팩') > 0:
                stc_tcd = 'SPAC'
            if row['종목명'] in ['미래에셋대우', '연우', '나우IB', '이오플로우']:
                stc_tcd = 'common'
            elif row['종목명'].count('우') > 0 and row['종목명'][-1] in ['우', 'B', 'C'] :
                stc_tcd = 'preferred'

            # sql 문 설정
            sql = "INSERT INTO findstock.sc_stc_basic (stc_id, mkt_nm, stc_tcd, stc_name, price, tot_value) " \
                  "VALUES ('%s', '%s', '%s', '%s', '%d', '%d')" \
                  % (row['종목코드'], mkt_nm, stc_tcd, row['종목명'], row['현재가'], row['시가총액'])

            try:
                db_class.execute(sql)
            except Exception as de:
                print("에러: 종목정보 저장시 에러. 종목코드: {}, 종목명: {}, 마켓구분: {}, 페이지: {}"
                      .format(row['종목코드'], row['종목명'], mkt_nm, page))
                print(de)
                pass
        # 커밋
        db_class.commit()


# main 처리
def set_stc_basic_info():

    # 거래일 체크
    day_class = dy_module.Day()
    if not day_class.trade_dy_yn():
        print("휴일 미수행")
        return

    # 시작메시지
    print("종목정보 수신시작")

    # 시작시간
    start_time = dy_module.now_dt("%Y-%m-%d %H:%M:%S")

    # 처리
    stock_values_delete()
    set_stc_basic_market_info(mkt_tcd=0)
    set_stc_basic_market_info(mkt_tcd=1)

    # 종료 시간
    end_time = dy_module.now_dt("%Y-%m-%d %H:%M:%S")

    # 종료메시지
    end_msg = "종목정보 수신 완료\n" + \
              "시작시각: {}\n".format(start_time) + \
              "종료시각: {}\n".format(end_time)
    print(end_msg)

    # 종료메시지송신
    end_msg_sn = dy_module.now_dt("%Y%m%d%H%M%S%f")
    send_message_to_friends(data=end_msg, msg_sn=end_msg_sn, destination='toAdmin')


if __name__ == '__main__':
    set_stc_basic_info()

