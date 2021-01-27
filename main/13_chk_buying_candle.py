# 추출된 매집봉이 유효한지 확인 한다.
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
from commonModule import db_module, dy_module
from collectData.get_daily_price_info import get_daily_price_info
from commonModule.telegram_module import send_message_to_friends


# DB 값 수정
def update_stock_candle_info(db_class, dy):
    # DB Insert
    try:
        sql = "UPDATE findstock.sc_stc_candle " \
              "SET available_yn = 'N' " \
              "WHERE dy < '%s'" % dy
        db_class.execute(sql)
        db_class.commit()
        return
    except Exception as de:
        print("에러: 과거 매집봉 유효여부 매집봉 수정시 에러. 일자: {}".format(dy))
        print(de)


# DB 값 수정
def update_stock_candle_each_info(db_class, dy, stc_id):
    # DB Insert
    try:
        sql = "UPDATE findstock.sc_stc_candle " \
              "SET available_yn = 'N' " \
              "WHERE dy = '%s' AND stc_id = '%s'" % (dy, stc_id)
        db_class.execute(sql)
        db_class.commit()
        return
    except Exception as de:
        print("에러: 매집봉 유효여부 수정시 에러. 일자: {}, 종목코드: {}".format(dy, stc_id))
        print(de)


# 매집봉 유효여부 판단
def unavailable_candle_yn(each_row):
    # 판별대상 데이터
    dy = each_row['dy']
    stc_id = each_row['stc_id']
    price = each_row['price']
    deal_qnt = each_row['deal_qnt']
    stop_loss_price = each_row['stop_loss_price']

    # 30일간 일별 가격정보
    daily_price_info = get_daily_price_info(stc_id, 30)

    # 비교대상 일별 가격정보
    compare_dy = dy[0:4] + '.' + dy[4:6] + '.' + dy[6:8]
    check_price_info = daily_price_info[daily_price_info['날짜'] > compare_dy]

    # 저가가 stop_loss_price 를 하회한 적이 있는지 확인
    is_under_stop_loss = check_price_info['저가'] < stop_loss_price

    # stop_loss_price 하회 여부
    if check_price_info[is_under_stop_loss].shape[0] > 0:
        return True

    # 거래량이 deal_qnt 의 50% 이상인 적이 있는지 확인
    is_upper_deal_qnt = check_price_info['거래량'] > deal_qnt*0.5

    # -5% 이상 하락한 적이 있는지 확인
    is_price_down = check_price_info['종가'] / check_price_info['시가'] < 0.95

    # 개래량 하락폭 동시 달성여부
    if check_price_info[is_upper_deal_qnt & is_price_down].shape[0] >0:
        return True

    return False


# main 처리
def chk_buying_candle():
    # 거래일 체크
    day_class = dy_module.Day()
    if not day_class.trade_dy_yn():
        print("휴일 미수행")
        return

    # 시작메시지
    print("매집봉 유효성 판별 시작!!!")

    # 시작시간
    start_time = dy_module.now_dt("%Y-%m-%d %H:%M:%S")

    # 당일 및 30전거래일
    dy = dy_module.now_dy()
    base_dy = day_class.cal_tr_dy(-30)

    # db 모듈
    db_class = db_module.Database()

    # 30일 경과한 매집봉은 관심에서 제외한다.
    update_stock_candle_info(db_class, base_dy)

    # 개별 대상건 조회(현시점 기준 유효한 매집봉)
    sql = "select a.dy, a.stc_id, a.price, a.deal_qnt, a.stop_loss_price " \
          "from findstock.sc_stc_candle a where a.available_yn = 'Y'"
    rows = db_class.execute_all(sql)

    # 조회된 건수 바탕으로 판별 및 설정
    for i, row in enumerate(rows):
        try:
            if i % 10 == 0:
                print("판단중.... 전체:", len(rows), "건, 현재: ", i, "건")

            # 판별대상 데이터
            dy = row['dy']
            stc_id = row['stc_id']

            # 판별 및 DB 값 수정
            if unavailable_candle_yn(row):
                # db 값 변경
                update_stock_candle_each_info(db_class, dy, stc_id)
                stc_id = row['stc_id']

        except Exception as ex:
            print("에러: 매집봉정보 입력시 에러. 일자: {}, 종목코드: {}".format(dy, stc_id))
            print(ex)

    # 최종커밋
    db_class.commit()

    # 종료 시간
    end_time = dy_module.now_dt("%Y-%m-%d %H:%M:%S")

    # 종료메시지
    end_msg = "매집봉 유효성 판별 종료!!!\n" + \
              "시작시각: {}\n".format(start_time) + \
              "종료시각: {}\n".format(end_time)
    print(end_msg)

    # 종료메시지송신
    end_msg_sn = dy_module.now_dt("%Y%m%d%H%M%S%f")
    send_message_to_friends(data=end_msg, msg_sn=end_msg_sn, destination='toAdmin')


if __name__ == "__main__":
    chk_buying_candle()
