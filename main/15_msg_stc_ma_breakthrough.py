import sys
import os
import traceback
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
from commonModule import db_module, dy_module
from collectData.get_detail_info import get_detail_info
from bizLogic.calculate_move_average import calculate_move_avg
from commonModule.telegram_module import set_stc_data, send_message_to_friends


# DB insert
def insert_stc_aram(db_class, dy, stc_id, price, msg_sn):
    # DB Insert
    try:
        sql = "INSERT INTO findstock.sc_stc_aram (dy, stc_id, judge_tcd, price, msg_sn) " \
              "VALUES ('%s', '%s', '%s', '%d', '%s')" % (dy, stc_id, 'maBreakthrough', price, msg_sn)
        db_class.execute(sql)
        db_class.commit()
        return
    except Exception as de:
        print("에러: 이평선 돌파 종목 판별/알림 정보 입력시 에러. 일자: {}, 종목코드: {}, 가격: {}".format(dy, stc_id, price))
        print(de)


# 이평선 돌파시 메시지 송신
def get_ma_and_send_message(in_stc_id=None):
    # db 모듈
    db_class = db_module.Database()

    # 당일
    dy = dy_module.now_dy()

    # data 초기화
    sql = "DELETE from findstock.sc_stc_aram WHERE dy = '%s' and judge_tcd = 'maBreakthrough'" % dy
    db_class.execute(sql)
    db_class.commit()

    # 대상건 조회
    sql = "select a.stc_id, b.stc_name, b.price, a.ma5, a.ma20, a.ma60, a.ma120, a.ma240 " \
          "from findstock.sc_stc_move_avg a, findstock.sc_stc_basic b, findstock.sc_stc_filter c " \
          "where a.stc_id = b.stc_id and a.stc_id = c.stc_id and c.helth_yn = 'Y' and b.tot_value > 500000000000"

    if in_stc_id is not None:
        sql = "select a.stc_id, b.stc_name, b.price, a.ma5, a.ma20, a.ma60, a.ma120, a.ma240 " \
              "from findstock.sc_stc_move_avg a, findstock.sc_stc_basic b " \
              "where a.stc_id = b.stc_id and a.stc_id = '%s'" % in_stc_id

    rows = db_class.executeAll(sql)

    # 조회된 건수 바탕으로 data 세팅 및 메시지 송신
    for row in rows:
        try:
            # 대상 데이터
            stc_id = row['stc_id']
            stc_name = row['stc_name']

            # 기존값
            old_now_price = row['price']
            old_ma5 = row['ma5']
            old_ma20 = row['ma20']
            old_ma60 = row['ma60']
            old_ma120 = row['ma120']
            old_ma240 = row['ma240']

            # 현재가 및 이동평균가격
            price_info = calculate_move_avg(stc_id, 0, 120).iloc[-1].fillna(0)
            now_price = get_detail_info(stc_id)['가격정보']['현재가'].iloc[0]
            ma5 = price_info['5일이평선']
            ma20 = price_info['20일이평선']
            ma60 = price_info['60일이평선']
            ma120 = price_info['120일이평선']
            ma240 = price_info['240일이평선']

            # 새로운 값 DB저장(이평선 정보)
            sql = "update stock_search.stock_move_avg " \
                  "set ma5 = '%d', ma20 = '%d', ma60= '%d', ma120 = '%d', ma240 = '%d'" \
                  "where stc_id = '%s'" % (ma5, ma20, ma60, ma120, ma240, stc_id)
            db_class.execute(sql)

            # 새로운 값 DB저장(현재가 정보)
            sql = "update stock_search.sc_stc_basic " \
                  "set price = '%d' where stc_id = '%s'" % (now_price, stc_id)
            db_class.execute(sql)
            db_class.commit()

            # 메시지조합
            yn_now = False
            yn_5 = False
            yn_20 = False
            yn_60 = False
            yn_120 = False

            msg_temp = ""
            msg_now = ""
            msg_5 = ""
            msg_20 = ""
            msg_60 = ""
            msg_120 = ""

            # 현재가 5일선돌파
            if old_now_price <= old_ma5 and now_price > ma5:
                msg_temp = msg_temp+"5 "
                yn_now = True

            # 현재가 20일선돌파
            if old_now_price <= old_ma20 and now_price > ma20:
                msg_temp = msg_temp+"20 "
                yn_now = True

            # 현재가 60일선돌파
            if old_now_price <= old_ma60 and now_price > ma60:
                msg_temp = msg_temp+"60 "
                yn_now = True

            # 현재가 120일선돌파
            if old_now_price <= old_ma120 and now_price > ma120:
                msg_temp = msg_temp+"120 "
                yn_now = True

            # 현재가 240일선돌파
            if old_now_price <= old_ma240 and now_price > ma240:
                msg_temp = msg_temp+"240 "
                yn_now = True

            # 메시지 조립
            if yn_now:
                msg_now = "현재가: " + msg_temp + "일선 돌파! \n"
            msg_temp = ""

            # 5일선 20일선돌파
            if old_ma5 <= old_ma20 and ma5 > ma20:
                msg_temp = msg_temp+"20 "
                yn_5 = True

            # 5일선 60일선돌파
            if old_ma5 <= old_ma60 and ma5 > ma60:
                msg_temp = msg_temp+"60 "
                yn_5 = True

            # 5일선 120일선돌파
            if old_ma5 <= old_ma120 and ma5 > ma120:
                msg_temp = msg_temp+"120 "
                yn_5 = True

            # 5일선 240일선돌파
            if old_ma5 <= old_ma240 and ma5 > ma240:
                msg_temp = msg_temp+"240 "
                yn_5 = True

            # 메시지 조립
            if yn_5:
                msg_5 = "5일선: " + msg_temp + "일선 돌파! \n"
            msg_temp = ""

            # # 20일선 60일선돌파
            # if old_ma20 <= old_ma60 and ma20 > ma60:
            #     msg_temp = msg_temp+"60 "
            #     yn_20 = True

            # 20일선 120일선돌파
            if old_ma20 <= old_ma120 and ma20 > ma120:
                msg_temp = msg_temp+"120 "
                yn_20 = True

            # # 20일선 240일선돌파
            # if old_ma20 <= old_ma240 and ma20 > ma240:
            #     msg_temp = msg_temp+"240 "
            #     yn_20 = True

            # 메시지 조립
            if yn_20:
                msg_20 = "20일선: " + msg_temp + "일선 돌파! \n"
            msg_temp = ""

            # 60일선 120일선돌파
            if old_ma60 <= old_ma120 and ma60 > ma120:
                msg_temp = msg_temp+"120 "
                yn_60 = True

            # 60일선 240일선돌파
            if old_ma60 <= old_ma240 and ma60 > ma240:
                msg_temp = msg_temp+"240 "
                yn_60 = True

            # 메시지 조립
            if yn_60:
                msg_60 = "60일선: " + msg_temp + "일선 돌파! \n"
            msg_temp = ""

            # 120일선 240일선돌파
            if old_ma120 <= old_ma240 and ma120 > ma240:
                msg_temp = msg_temp+"240 "
                yn_120 = True

            # 메시지 조립
            if yn_120:
                msg_120 = "120일선: " + msg_temp + "일선 돌파! \n"

            # 최종 메시지 조립
            msg_final = msg_now+msg_5+msg_20+msg_60+msg_120
            msg_final = msg_20

            # 메시지 송신
            # if yn_now or yn_5 or yn_20 or yn_60 or yn_120:
            if yn_20:
                # 메시지순번(시간값으로 대신함)
                msg_sn = dy_module.now_dt("%Y%m%d%H%M%S%f")

                # 메시지송신
                msg = set_stc_data(stc_id=stc_id, stc_name=stc_name, text=msg_final)
                send_message_to_friends(msg, msg_sn)

                # db insert
                insert_stc_aram(db_class, dy, stc_id, now_price, msg_sn)

        except Exception as ex:
            print("에러: 이평선 돌파 값 저장 및 메시지 송신 에러. 종목코드: {}".format(stc_id))
            print(ex)

    db_class.commit()

    return


def msg_stc_ma_breakthrough(in_stc_id=None):

    # 거래일 체크
    day_class = dy_module.Day()
    if not day_class.trade_dy_yn():
        print("휴일 미수행")
        return

    # 시작메시지
    print("이평선 돌파 메시지 송신 시작!!!")

    # 시작시간
    start_time = dy_module.now_dt("%Y-%m-%d %H:%M:%S")

    # 프로세스 수행
    get_ma_and_send_message(in_stc_id)

    # 종료 시간
    end_time = dy_module.now_dt("%Y-%m-%d %H:%M:%S")

    # 종료메시지
    print("이평선 돌파 메시지 송신 종료!!!")
    print("시작시각: ", start_time)
    print("종료시각: ", end_time)


if __name__ == "__main__":
    msg_stc_ma_breakthrough()
