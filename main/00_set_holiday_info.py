# 휴일정보를 가져와서 일자 테이블에 휴일 정보 update 한다.
from commonModule import db_module, dy_module
from collectData.get_holiday_info import get_holiday_info


# 연도별 휴일정보 저장
def set_year_holiday_info(year):

    # DB 모듈선언
    db_class = db_module.Database()

    # 휴일탐색
    holidays = get_holiday_info(year)

    # 건수 없는 경우 리턴
    if holidays is None:
        print('처리건수: 0건')
        return

    # 휴일처리
    for holiday in holidays:
        # 일자
        dy = holiday['locdate']

        # 거래일여부
        if holiday['isHoliday'] == 'Y':
            tr_dy_yn = 'N'
        else:
            tr_dy_yn = 'Y'

        # 비고
        remark = holiday['dateName']

        # 획득한 휴일정보 update
        sql = "UPDATE findstock.cm_day_info SET tr_dy_yn = '%s', remark = '%s' " \
              "WHERE dy = '%s'" % (tr_dy_yn, remark, dy)
        db_class.execute(sql)
        db_class.commit()

    # 처리건수 확인
    print('처리건수: '+str(len(holidays))+'건')


# main 처리
def set_holiday_info():
    # 시작메시지
    print("연도별 휴일정보 저장 시작!!!")

    # 시작시간
    start_time = dy_module.now_dt("%Y-%m-%d %H:%M:%S")

    # 처리
    set_year_holiday_info(year='2022')

    # 종료 시간
    end_time = dy_module.now_dt("%Y-%m-%d %H:%M:%S")

    # 종료메시지
    print("연도별 휴일정보 저장 종료!!!")
    print("시작시각: ", start_time)
    print("종료시각: ", end_time)


if __name__ == '__main__':
    set_holiday_info()
