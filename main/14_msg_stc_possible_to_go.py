# 매집봉 나타낸 주식을 대상으로 이평선 기반으로 차트를 분석한다.
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
from commonModule import db_module, dy_module
from bizLogic.analysis_ma_chart import analysis_ma_chart
from commonModule.telegram_module import set_stc_data, send_message_to_friends


# DB insert
def insert_stc_alarm(db_class, dy, stc_id, judge_tcd, price, msg_sn):
    # DB Insert
    try:
        sql = "INSERT INTO findstock.sc_stc_alarm (dy, alarm_sn, stc_id, judge_tcd, price, msg_sn) " \
              "VALUES ('%s', (select ifnull(max(x.alarm_sn),0)+1 from findstock.sc_stc_alarm x where dy='%s'), " \
              "'%s', '%s', '%d', '%s')" % (dy, dy, stc_id, judge_tcd, price, msg_sn)
        db_class.execute(sql)
        db_class.commit()
        return
    except Exception as de:
        print("에러: 상승예상 종목 판별/알림 정보 입력시 에러. 일자: {}, 종목코드: {}, 가격: {}".format(dy, stc_id, price))
        print(de)


# 상승가능여부 판별
def judge_stc_to_go_1(stc_id, now_price):

    # 20일선 횡보 또는 상승 여부
    ma20_analysis = analysis_ma_chart(stc_id, 20, 20)
    if ma20_analysis['high_trend'] < 0 or ma20_analysis['low_trend'] < 0:
        return {"judge_to_go_yn": False}

    # 60일선 횡보 또는 상승 여부
    ma60_analysis = analysis_ma_chart(stc_id, 60, 60)
    if ma60_analysis['high_trend'] < 0 or ma60_analysis['low_trend'] < 0:
        return {"judge_to_go_yn": False}

    # 20일선과 종가 이격도 체크
    ma20_last = ma20_analysis["local_max_min_info"]["원근값"][1]
    if now_price / ma20_last > 1.04 or now_price / ma20_last < 0.96:
        return {"judge_to_go_yn": False}

    # 5일선 흐름 판정: 상승삼각형 또는 횡보 판정
    ma05_analysis = analysis_ma_chart(stc_id, 5, 60)
    if not ma05_analysis['high_trend'] == 0:
        return {"judge_to_go_yn": False}
    if ma05_analysis['low_trend'] < 0:
        return {"judge_to_go_yn": False}

    # 5일선으로 전고점을 추측해 본다.
    if len(ma05_analysis["local_max_min_info"]["극대값"]) == 0:
        before_high_value = ma05_analysis["local_max_min_info"]["원근값"][-1]
    else:
        before_high_value = ma05_analysis["local_max_min_info"]["극대값"][-1]

    # 현재가가 전고점 근접 또는 돌파 확인
    if now_price/before_high_value < 0.98:
        return {"judge_to_go_yn": False}

    # 모든 조건 충족시 True 리턴
    return {"judge_to_go_yn": True}


# 상승가능여부 판별
def judge_stc_to_go_2(stc_id, now_price):

    # 20일선 횡보 또는 상승 여부
    ma20_analysis = analysis_ma_chart(stc_id, 20, 20)
    if ma20_analysis['high_trend'] < 0 or ma20_analysis['low_trend'] < 0:
        return {"judge_to_go_yn": False}

    # 60일선 횡보 또는 상승 여부
    ma60_analysis = analysis_ma_chart(stc_id, 60, 60)
    if ma60_analysis['high_trend'] < 0 or ma60_analysis['low_trend'] < 0:
        return {"judge_to_go_yn": False}

    # 5일선 흐름 판정: 상승삼각형 또는 횡보 판정
    ma05_analysis = analysis_ma_chart(stc_id, 5, 60)
    if not ma05_analysis['high_trend'] == 0:
        return {"judge_to_go_yn": False}
    if ma05_analysis['low_trend'] < 0:
        return {"judge_to_go_yn": False}

    # 5일선으로 전고점을 추측해 본다.
    if len(ma05_analysis["local_max_min_info"]["극대값"]) == 0:
        before_high_value = ma05_analysis["local_max_min_info"]["원근값"][-1]
    else:
        before_high_value = ma05_analysis["local_max_min_info"]["극대값"][-1]

    # 현재가가 전고점 근접 또는 돌파 확인
    if now_price/before_high_value < 0.98:
        return {"judge_to_go_yn": False}

    # 모든 조건 충족시 True 리턴
    return {"judge_to_go_yn": True}


# main 처리
def set_stc_possible_to_go():
    # 거래일 체크
    day_class = dy_module.Day()
    if not day_class.trade_dy_yn():
        print("휴일 미수행")
        return

    # 시작메시지
    print("상승예상 종목 판별/알림 시작")

    # 시작시간
    start_time = dy_module.now_dt("%Y-%m-%d %H:%M:%S")

    # 당일, 대상건 조회시 제외 기준일
    dy = dy_module.now_dy()
    except_dy = day_class.cal_tr_dy(-5)

    # db 모듈
    db_class = db_module.Database()

    # data 초기화
    sql = "DELETE from findstock.sc_stc_alarm WHERE dy = '%s' and judge_tcd in ('possToGo', 'captureCandle')" % dy
    db_class.execute(sql)
    db_class.commit()

    # 대상건 조회1(현재 유효한 매집봉 type_1, 5일이내 같은 알림 보낸 종목은 제외)
    select_sql_1 = "select a.stc_id, b.stc_name, b.price, a.stop_loss_price, a.dy " \
                   "from findstock.sc_stc_candle a, findstock.sc_stc_basic b " \
                   "   , (select a.stc_id, max(a.dy) as dy " \
                   "        from findstock.sc_stc_candle a, findstock.sc_stc_basic b " \
                   "       where a.stc_id = b.stc_id and a.available_yn = 'Y' AND a.candle_tcd = 'type_1' " \
                   "       group by a.stc_id) c " \
                   "where a.stc_id = b.stc_id  " \
                   "and a.stc_id = c.stc_id " \
                   "and a.dy = c.dy  " \
                   "and a.available_yn = 'Y' AND a.candle_tcd = 'type_1'  " \
                   "AND a.stc_id NOT IN(" \
                   "select stc_id from findstock.sc_stc_alarm where dy >= '%s'" \
                   "and judge_tcd = 'possToGo'" \
                   ")" % except_dy

    # 대상건 조회2(현재 유효한 매집봉 type_2, 당일발생 매집봉의 종목만 조회회)
    select_sql_2 = "select a.stc_id, b.stc_name, b.price, count(*) as cnt, " \
                   "(select stop_loss_price from findstock.sc_stc_candle x " \
                   "where x.stc_id = a.stc_id and x.dy = (select max(dy) " \
                   "from findstock.sc_stc_candle xx where xx.stc_id = x.stc_id )) as stop_loss_price " \
                   "from findstock.sc_stc_candle a, findstock.sc_stc_basic b " \
                   "where a.stc_id = b.stc_id and a.candle_tcd = 'type_2' and a.available_yn = 'Y' " \
                   "and a.stc_id in (select stc_id from findstock.sc_stc_candle ia where ia.dy = '%s') " \
                   "group by a.stc_id" % dy

    rows_1 = db_class.execute_all(select_sql_1)
    rows_2 = db_class.execute_all(select_sql_2)

    # 조회된 건수 바탕으로 판별 및 송신(type_1)
    for i, row in enumerate(rows_1):
        try:
            if i % 10 == 0:
                print("판단중.... 전체:", len(rows_1)+len(rows_2), "건, 현재: ", i, "건")

            # 판별대상 데이터
            stc_id = row['stc_id']
            stc_name = row['stc_name']
            now_price = row['price']
            stop_loss_price = row['stop_loss_price']

            # 판별 (매집봉 타입에 따라 다른 판별수행)
            judge_result = judge_stc_to_go_1(stc_id, now_price)['judge_to_go_yn']

            # 및 DB 값 수정
            if judge_result:
                # 메시지순번(시간값으로 대신함)
                msg_sn = dy_module.now_dt("%Y%m%d%H%M%S%f")

                # db insert
                insert_stc_alarm(db_class, dy, stc_id, 'possToGo', now_price, msg_sn)

                # 메시지송신
                text_msg = "상승예상 종목\n손절가: {:,}원".format(stop_loss_price)

                msg = set_stc_data(stc_id=stc_id, stc_name=stc_name, text=text_msg)
                send_message_to_friends(msg, msg_sn)

        except Exception as ex:
            print("에러: 상승예상 종목(type_1) 추출시 에러. 일자: {}, 종목코드: {}, 가격: {}".format(dy, stc_id, now_price))
            print(ex)

    # 메시지 송신 여부(type_2) 송신에 사용
    msg_yn = False

    # 송신메시지
    msg = "[{}년{}월{}일 매집봉 출현 종목]\n\n".format(dy[0:4], dy[4:6], dy[6:8])

    # 조회된 건수 바탕으로 판별 및 송신(type_2)
    for j, row in enumerate(rows_2):
        try:
            if (len(rows_1)+j) % 10 == 0:
                print("판단중.... 전체:", len(rows_1)+len(rows_2), "건, 현재: ", len(rows_1)+j, "건")

            # 판별대상 데이터
            stc_id = row['stc_id']
            stc_name = row['stc_name']
            now_price = row['price']
            candle_cnt = row['cnt']
            stop_loss_price = row['stop_loss_price']

            # 판별 (매집봉 타입에 따라 다른 판별수행)
            judge_result = judge_stc_to_go_2(stc_id, now_price)['judge_to_go_yn']

            # 및 DB 값 수정
            if judge_result:
                # 메시지 송신 여부
                msg_yn = True

                # 메시지순번(시간값으로 대신함)
                msg_sn = dy_module.now_dt("%Y%m%d%H%M%S%f")

                # db insert
                insert_stc_alarm(db_class, dy, stc_id, 'captureCandle', now_price, msg_sn)

                # 개별 메시지 내용 저장
                text_msg = "매집봉 출현 종목\n손절가: {:,}원".format(stop_loss_price)
                data_msg = set_stc_data(stc_id=stc_id, stc_name=stc_name, text=text_msg)
                insert_sql = "insert into findstock.cm_sent_msg (dy, sn, tcd, tm, cn) " \
                             "values ('%s', '%s', '%s','%s', '%s')" % (dy, msg_sn, 'toGuest', dy_module.now_tm(), data_msg)

                db_class.execute(insert_sql)
                db_class.commit()

                # 메시지송신용 문장 append
                stc_msg = "[{}]({}회)손절가: {:,}원\n".format(stc_name, candle_cnt, stop_loss_price)
                url_msg = "https://finance.naver.com/item/main.nhn?code={}\n\n".format(stc_id)
                msg = msg+stc_msg+url_msg

        except Exception as ex:
            print("에러: 상승예상 종목(type_2) 추출시 에러. 일자: {}, 종목코드: {}, 가격: {}".format(dy, stc_id, now_price))
            print(ex)

    # 메시지 송신
    if msg_yn:
        # 메시지순번(시간값으로 대신함)
        msg_sn = dy_module.now_dt("%Y%m%d%H%M%S%f")
        send_message_to_friends(msg, msg_sn)

    # 종료 커밋
    db_class.commit()

    # 종료 시간
    end_time = dy_module.now_dt("%Y-%m-%d %H:%M:%S")

    # 종료메시지
    end_msg = "상승예상 종목 추출 및 메시지 송신 완료\n" + \
              "시작시각: {}\n".format(start_time) + \
              "종료시각: {}\n".format(end_time)
    print(end_msg)

    # 종료메시지송신
    end_msg_sn = dy_module.now_dt("%Y%m%d%H%M%S%f")
    send_message_to_friends(data=end_msg, msg_sn=end_msg_sn, destination='toAdmin')


if __name__ == "__main__":
    set_stc_possible_to_go()
    # print(judge_stc_to_go_2('009780', 11900))
