# 소형우량주 중에서 매집봉이 나타난 종목을 추출하여 db에 저장한다.
from commonModule import db_module, dy_module
from bizLogic.search_buying_candle import search_buying_candle
from collectData.get_daily_price_info import get_daily_price_info


# DB 값 수정
def update_stock_filter_info(db_class, dy, stc_id, price, stop_loss_price):
    # DB Insert
    try:
        sql = "INSERT INTO findstock.sc_stc_candle (dy, stc_id, price, stop_loss_price) " \
              "VALUES ('%s', '%s', '%d', '%d')" % (dy, stc_id, price, stop_loss_price)
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
    print("소형우량주 매집봉 판별/입력 시작!!!")

    # 시작시간
    start_time = dy_module.now_dt("%Y-%m-%d %H:%M:%S")

    # 당일
    dy = dy_module.now_dy()

    # db 모듈
    db_class = db_module.Database()

    # 초기화
    sql = "DELETE from findstock.sc_stc_candle WHERE dy = '%s'" % dy
    db_class.execute(sql)
    db_class.commit()

    # 대상건 조회(소형 우량주주 only)
    sql = "select a.stc_id, a.stc_name, a.price " \
          "from findstock.sc_stc_basic a, findstock.sc_stc_filter b " \
          "where a.stc_id = b.stc_id and b.helth_yn = 'Y' AND a.tot_value < 500000000000"
    rows = db_class.execute_all(sql)

    # 조회된 건수 바탕으로 판별 및 송신
    for i, row in enumerate(rows):
        try:
            if i % 10 == 0:
                print("판단중.... 전체:", len(rows), "건, 현재: ", i, "건")

            # 판별대상 데이터
            stc_id = row['stc_id']
            price = row['price']

            # 판별 및 DB 값 수정
            if search_buying_candle(stc_id)['buying_candle_yn']:

                # 손절라인(과거 20 거래일 가격정보 에서 최저가)
                stop_loss_price = get_daily_price_info(stc_id, 20)['저가'].min()

                # db 값 변경
                update_stock_filter_info(db_class, dy, stc_id, price, stop_loss_price)

        except Exception as ex:
            print("에러: 매집봉정보 입력시 에러. 일자: {}, 종목코드: {}, 가격: {}".format(dy, stc_id, price))
            print(ex)

    # 종료 메시지
    db_class.commit()

    # 종료 시간
    end_time = dy_module.now_dt("%Y-%m-%d %H:%M:%S")

    # 종료메시지
    print("소형우량주 매집봉 판별/입력 종료!!!")
    print("시작시각: ", start_time)
    print("종료시각: ", end_time)


if __name__ == "__main__":
    set_stc_candle_info()
