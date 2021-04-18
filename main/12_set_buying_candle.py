# 소형우량주 중에서 매집봉이 나타난 종목을 추출하여 db에 저장한다.
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
from commonModule import db_module, dy_module
from bizLogic.search_buying_candle import search_buying_candle_1, search_buying_candle_2
from commonModule.telegram_module import send_message_to_friends


# DB 값 입력
def insert_stock_candle_info(db_class, dy, stc_id, candle_tcd, price, deal_qnt, stop_loss_price):
    # DB Insert
    try:
        sql = "INSERT INTO findstock.sc_stc_candle " \
              "(dy, stc_id, candle_tcd, price, deal_qnt, stop_loss_price, available_yn) " \
              "VALUES ('%s', '%s', '%s', '%d', '%d', '%d', 'Y')" % \
              (dy, stc_id, candle_tcd, price, deal_qnt, stop_loss_price)
        db_class.execute(sql)
        db_class.commit()
        return
    except Exception as de:
        print("에러: 소형우량주 매집봉 입력시 에러. 일자: {}, 종목코드: {}, 가격: {}".format(dy, stc_id, price))
        print(de)


# main 처리
def set_stc_candle_info():
    # 거래일 체크
    day_class = dy_module.Day()
    if not day_class.trade_dy_yn():
        print("휴일 미수행")
        return

    # 시작메시지
    print("소형우량주 매집봉 판별/입력 시작")

    # 시작시간
    start_time = dy_module.now_dt("%Y-%m-%d %H:%M:%S")

    # 당일/전거래일
    nw_dy = dy_module.now_dy()
    bf_dy = day_class.cal_tr_dy(-1)

    # db 모듈
    db_class = db_module.Database()

    # 초기화
    sql = "DELETE from findstock.sc_stc_candle WHERE dy = '%s' and candle_tcd = 'type_1'" % bf_dy
    db_class.execute(sql)
    sql = "DELETE from findstock.sc_stc_candle WHERE dy = '%s' and candle_tcd = 'type_2'" % nw_dy
    db_class.execute(sql)
    db_class.commit()

    # 대상건 조회(소형 우량주 only)
    sql = "select a.stc_id, a.stc_name, a.price " \
          "from findstock.sc_stc_basic a, findstock.sc_stc_filter b " \
          "where a.stc_id = b.stc_id and b.helth_yn = 'Y' AND a.tot_value < 500000000000"
    rows = db_class.execute_all(sql)

    # 조회된 건수 바탕으로 판별 및 설정
    for i, row in enumerate(rows):
        try:
            if i % 10 == 0:
                print("판단중.... 전체:", len(rows), "건, 현재: ", i, "건")

            # 판별대상 데이터
            stc_id = row['stc_id']

            # 판별 및 DB 값 수정(type_1)
            buying_candle = search_buying_candle_1(stc_id)
            if buying_candle['buying_candle_yn']:

                # 매집봉 발생일 거래량 및 가격
                deal_qnt = buying_candle['prices_info']['거래량']
                price = buying_candle['prices_info']['종가']

                # 손절라인(매집봉 이전 10 거래일 중 최저가, 종가의 95% 중 큰 값)
                stop_loss_price = max(buying_candle['min_price_of_ten'], price*0.95)

                # 매집봉 발생일자
                candle_dy = buying_candle['prices_info']['날짜'].replace('.', '')

                # db 값 변경
                insert_stock_candle_info(db_class, candle_dy, stc_id, 'type_1', price, deal_qnt, stop_loss_price)

            # 판별 및 DB 값 수정(type_2)
            buying_candle = search_buying_candle_2(stc_id)
            if buying_candle['buying_candle_yn']:

                # 매집봉 발생일 거래량 및 가격
                deal_qnt = buying_candle['prices_info']['거래량']
                price = buying_candle['prices_info']['종가']

                # 손절라인(매집봉 이전 10 거래일 중 최저가, 종가의 95% 중 큰 값)
                stop_loss_price = max(buying_candle['min_price_of_ten'], price*0.95)

                # 매집봉 발생일자
                candle_dy = buying_candle['prices_info']['날짜'].replace('.', '')

                # db 값 변경
                insert_stock_candle_info(db_class, candle_dy, stc_id, 'type_2', price, deal_qnt, stop_loss_price)

        except Exception as ex:
            print("에러: 매집봉정보 입력시 에러. 일자: {}, 종목코드: {}, 가격: {}".format(candle_dy, stc_id, price))
            print(ex)

    # 최종커밋
    db_class.commit()

    # 종료 시간
    end_time = dy_module.now_dt("%Y-%m-%d %H:%M:%S")

    # 종료메시지
    end_msg = "소형우량주 매집봉 판별/입력 완료\n" + \
              "시작시각: {}\n".format(start_time) + \
              "종료시각: {}\n".format(end_time)
    print(end_msg)

    # 종료메시지송신
    end_msg_sn = dy_module.now_dt("%Y%m%d%H%M%S%f")
    send_message_to_friends(data=end_msg, msg_sn=end_msg_sn, destination='toAdmin')


if __name__ == "__main__":
    set_stc_candle_info()
