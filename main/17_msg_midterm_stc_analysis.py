import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
from commonModule import db_module, dy_module
from collectData.get_detail_info import get_detail_info
from collectData.get_stc_market_condition import get_stc_market_condition
from collectData.get_disclosure_info import get_disclosure_info
from commonModule.telegram_module import set_stc_data, send_message_to_friends


# DB insert
def insert_stc_alarm(db_class, dy, stc_id, price, msg_sn):
    # DB Insert
    try:
        sql = "INSERT INTO findstock.sc_stc_alarm (dy, alarm_sn, stc_id, judge_tcd, price, msg_sn) " \
              "VALUES ('%s', (select ifnull(max(x.alarm_sn),0)+1 from findstock.sc_stc_alarm x where dy='%s'), " \
              "'%s', '%s', '%d', '%s')" % (dy, dy, stc_id, 'midtermPositive', price, msg_sn)
        db_class.execute(sql)
        db_class.commit()
        return
    except Exception as de:
        print("에러: 이평선 돌파 종목 판별/알림 정보 입력시 에러. 일자: {}, 종목코드: {}, 가격: {}".format(dy, stc_id, price))
        print(de)


# 판별
def midterm_stc_analysis(stc_id):
    # 분기 영업이익
    quarter_profit = get_detail_info(stc_id)['분기재무정보']['영업이익'].dropna()

    # 분기정보 없으면 false
    if quarter_profit.shape[0] == 0:
        return False

    # 마지막은 흑자상태여야 함.
    if quarter_profit[-1] <= 0:
        return False

    # 과거 분기 영업이익 적자 존재시 영업익 일정정도 상승이 있어야 함.
    if quarter_profit[quarter_profit <= 0].shape[0] > 0:
        if (quarter_profit[-1] - quarter_profit[0])/quarter_profit[-1] < 0.2:
            return False
    # 과거 분기 영업이익 적자 미 존재시 영업익 큰상승이 있어야 함.
    else:
        if quarter_profit[-1] < quarter_profit[0]*2:
            return False

    # 유통주식수가 30% 미만이어야 함
    outstanding_ratio = get_stc_market_condition(stc_id)['유동주식수/비율(보통주)'].iloc[0].split('/')[1].strip()
    if float(outstanding_ratio) >= 30:
        return False

    # 공시정보 추출 위한 6개월 전거래일 추출
    day_class = dy_module.Day()
    the_day_six_month_ago = day_class.cal_tr_dy(-120)

    # 과거 6개월간 공시 추출
    df_disclosure = get_disclosure_info(stc_id, the_day_six_month_ago)

    # 지정된 기간동안 유상증자 없어야 함
    judge = df_disclosure[df_disclosure['제목'].str.contains('유상증자')].shape[0]
    if judge > 0:
        return False

    # 지정된 기간동안 전환사채 없어야 함
    judge = df_disclosure[df_disclosure['제목'].str.contains('전환사채')].shape[0]
    if judge > 0:
        return False

    return True


# 중기투자 주식 판단
def msg_midterm_stc_analysis():
    # 거래일 체크
    day_class = dy_module.Day()
    if not day_class.trade_dy_yn():
        print("휴일 미수행")
        return

    # 시작메시지
    print("중기투자 주식 판단 시작")

    # 시작시간
    start_time = dy_module.now_dt("%Y-%m-%d %H:%M:%S")

    # db 모듈
    db_class = db_module.Database()

    # 당일, 예외 기준일
    dy = dy_module.now_dy()
    except_dy = day_class.cal_tr_dy(-20)

    # data 초기화
    sql = "DELETE from findstock.sc_stc_alarm WHERE dy = '%s' and judge_tcd = 'midtermPositive'" % dy
    db_class.execute(sql)
    db_class.commit()

    # 대상건 조회(재무적 우량주 only, 20영업일 이내에 동일 메시지 송신 제외)
    sql = "select a.stc_id, a.stc_name, a.price " \
          "from findstock.sc_stc_basic a, findstock.sc_stc_filter b " \
          "where a.stc_id = b.stc_id and b.helth_yn = 'Y' " \
          "AND a.stc_id NOT IN(" \
          "select stc_id from findstock.sc_stc_alarm where dy >= '%s'" \
          "and judge_tcd = 'midtermPositive'" \
          ")" % except_dy
    rows = db_class.execute_all(sql)

    # 조회된 주식 대상 판단
    for i, row in enumerate(rows):
        try:
            if i % 10 == 0:
                print("판단중.... 전체:", len(rows), "건, 현재: ", i, "건")

            # 판별대상 데이터
            stc_id = row['stc_id']
            stc_name = row['stc_name']
            now_price = row['price']

            # 판단 후 메지시 송신
            if midterm_stc_analysis(stc_id):
                # 메시지순번(시간값으로 대신함)
                msg_sn = dy_module.now_dt("%Y%m%d%H%M%S%f")

                # db insert
                insert_stc_alarm(db_class, dy, stc_id, now_price, msg_sn)

                # 메시지송신
                text_msg = "중기 관점 추천 종목"

                msg = set_stc_data(stc_id=stc_id, stc_name=stc_name, text=text_msg)
                send_message_to_friends(msg, msg_sn)

        except Exception as ex:
            print("에러: 중기투자 주식 판단 에러. 종목코드: {}".format(stc_id))
            print(ex)

    # 종료 커밋
    db_class.commit()

    # 종료 시간
    end_time = dy_module.now_dt("%Y-%m-%d %H:%M:%S")

    # 종료메시지
    end_msg = "중기투자 주식 판단 및 메시지 송신 완료\n" + \
              "시작시각: {}\n".format(start_time) + \
              "종료시각: {}\n".format(end_time)
    print(end_msg)

    # 종료메시지송신
    end_msg_sn = dy_module.now_dt("%Y%m%d%H%M%S%f")
    send_message_to_friends(data=end_msg, msg_sn=end_msg_sn, destination='toAdmin')


if __name__ == "__main__":
    msg_midterm_stc_analysis()
    # print(midterm_stc_analysis('112610'))


