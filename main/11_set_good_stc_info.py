# 소형/대형/특정 우량주 정보를 필터링 한다.
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
from commonModule import db_module, dy_module
from bizLogic.filter_good_condition import filter_good_condition


# DB 값 수정
def update_stock_filter_info(db_class, stc_id):

    # DB Insert
    try:
        sql = "INSERT INTO findstock.sc_stc_filter (stc_id, helth_yn) VALUES ('%s', 'Y')" % stc_id
        db_class.execute(sql)
        db_class.commit()
        return
    except Exception as de:
        print("에러: 우량주 필터링 입력시 에러. 종목코드: {}".format(stc_id))
        print(de)


# main 처리
def set_good_stc_info():
    # 거래일 체크
    day_class = dy_module.Day()
    if not day_class.trade_dy_yn():
        print("휴일 미수행")
        return

    # 시작메시지
    print("우량주 필터링 시작!!!")

    # 시작시간
    start_time = dy_module.now_dt("%Y-%m-%d %H:%M:%S")

    # db 모듈
    db_class = db_module.Database()

    # 초기화
    sql = "DELETE from findstock.sc_stc_filter"
    db_class.execute(sql)
    db_class.commit()

    # 대상건 조회(보통주 only)
    sql = "SELECT stc_id, stc_name FROM findstock.sc_stc_basic WHERE stc_tcd = 'common'"
    rows = db_class.execute_all(sql)

    # 조회된 건수 바탕으로 판별 및 송신
    for i, row in enumerate(rows):
        try:
            if i % 10 == 0:
                print("판단중.... 전체:", len(rows), "건, 현재: ", i, "건")

            # 판별대상 데이터
            stc_id = row['stc_id']
            stc_name = row['stc_name']

            # 판별 및 DB 값 수정
            if filter_good_condition(stc_id):

                # db 값 변경
                update_stock_filter_info(db_class, stc_id)

        except Exception as ex:
            print("에러: 우량주 필터링 판별시 에러. 종목코드: {}, 종목명: {}".format(stc_id, stc_name))
            print(ex)

    # 종료 메시지
    db_class.commit()

    # 종료 시간
    end_time = dy_module.now_dt("%Y-%m-%d %H:%M:%S")

    # 종료메시지
    print("우량주 필터링 종료!!!")
    print("시작시각: ", start_time)
    print("종료시각: ", end_time)


if __name__ == "__main__":
    set_good_stc_info()
