# 종목의 이동평균선을 저장한다.
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
from commonModule import db_module, dy_module
from bizLogic.calculate_move_average import calculate_move_avg
from commonModule.telegram_module import send_message_to_friends


# 이평선 정보 및 현재가 가져오기
def get_stc_ma_and_insert(in_stc_id=None):
    # db 모듈
    db_class = db_module.Database()

    # data 초기화
    if in_stc_id is not None:
        sql = "DELETE from findstock.sc_stc_move_avg WHERE stc_id = '%s'" % in_stc_id
    else:
        if len(sys.argv) > 1:
            if sys.argv[1] == 'other_day':
                sql = "DELETE from findstock.sc_stc_move_avg a where exists ( " \
                      "select 'x' from findstock.sc_stc_filter z where z.stc_id = a.stc_id and z.helth_yn = 'Y')"
            elif sys.argv[1] == 'friday':
                sql = "DELETE from findstock.sc_stc_move_avg"
        else:
            sql = "DELETE from findstock.sc_stc_move_avg"
    db_class.execute(sql)
    db_class.commit()

    # 대산 종목 조회
    if in_stc_id is not None:
        sql = "SELECT stc_id FROM findstock.sc_stc_basic WHERE stc_id = '%s'" % in_stc_id
    else:
        if len(sys.argv) > 1:
            if sys.argv[1] == 'other_day':
                sql = "SELECT a.stc_id FROM findstock.sc_stc_basic a, findstock.sc_stc_filter b " \
                      "where a.stc_id = b.stc_id and b.helth_yn = 'Y'"
            elif sys.argv[1] == 'friday':
                sql = "SELECT stc_id FROM findstock.sc_stc_basic "
        else:
            sql = "SELECT stc_id FROM findstock.sc_stc_basic "
    rows = db_class.execute_all(sql)

    # 조회된 건수 바탕으로 data 세팅
    for i, row in enumerate(rows):
        try:
            if i % 10 == 0:
                print("이평선정보 계산 및 저장중.... 전체:", len(rows), "건, 현재: ", i, "건")

            # 대상 데이터
            stc_id = row['stc_id']

            # 이동평균가격
            price_info = calculate_move_avg(stc_id, 0, 120).iloc[-1].fillna(0)
            ma5 = price_info['5일이평선']
            ma20 = price_info['20일이평선']
            ma60 = price_info['60일이평선']
            ma120 = price_info['120일이평선']
            ma240 = price_info['240일이평선']

            # 이평선정보 저장
            sql = "insert into findstock.sc_stc_move_avg (stc_id , ma5, ma20, ma60, ma120, ma240) " \
                  "values( '%s','%d','%d','%d','%d','%d')" % (stc_id, ma5, ma20, ma60, ma120, ma240)
            db_class.execute(sql)
            db_class.commit()
        except Exception as ex:
            print("에러: 이평선정보 계산 및 저장중 에러. 종목코드: {}".format(stc_id))
            print(ex)

    db_class.commit()
    print("이평선정보 계산 및 저장 완료")
    return


def set_stc_ma(in_stc_id=None):
    # 거래일 체크
    day_class = dy_module.Day()
    if not day_class.trade_dy_yn():
        print("휴일 미수행")
        return

    # 시작메시지
    print("종목별 이동평균 가격 저장 시작!!!")

    # 시작시간
    start_time = dy_module.now_dt("%Y-%m-%d %H:%M:%S")

    # 프로세스 수행
    get_stc_ma_and_insert(in_stc_id)

    # 종료 시간
    end_time = dy_module.now_dt("%Y-%m-%d %H:%M:%S")

    # 종료메시지
    end_msg = "종목별 이동평균 가격 저장 종료!!!\n" + \
              "시작시각: {}\n".format(start_time) + \
              "종료시각: {}\n".format(end_time)
    print(end_msg)

    # 종료메시지송신
    end_msg_sn = dy_module.now_dt("%Y%m%d%H%M%S%f")
    send_message_to_friends(data=end_msg, msg_sn=end_msg_sn, destination='toAdmin')


if __name__ == "__main__":
    set_stc_ma()
