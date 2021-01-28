# 휴일정보를 가져와서 일자 테이블에 휴일 정보 update 한다.
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
from commonModule import db_module, dy_module
from collectData.get_holiday_info import get_holiday_info
from commonModule.telegram_module import send_message_to_friends


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

    # 처리건수 return
    return len(holidays)


# main 처리
def set_holiday_info():
    # 시작메시지
    print("연도별 휴일정보 저장 시작")

    # 시작시간
    start_time = dy_module.now_dt("%Y-%m-%d %H:%M:%S")

    # 입력연도 설정
    if len(sys.argv) > 1:
        in_year = sys.argv[1]
    else:
        in_year = str(int(dy_module.now_dy("%Y"))+1)

    # 처리
    process_cnt = set_year_holiday_info(year=in_year)

    # 종료 시간
    end_time = dy_module.now_dt("%Y-%m-%d %H:%M:%S")

    # 종료메시지
    end_msg = "연도별 휴일정보 저장 완료\n" + \
              "시작시각: {}\n".format(start_time) + \
              "종료시각: {}\n".format(end_time) + \
              "처리건수: {}건".format(process_cnt)
    print(end_msg)

    # 종료메시지송신
    end_msg_sn = dy_module.now_dt("%Y%m%d%H%M%S%f")
    send_message_to_friends(data=end_msg, msg_sn=end_msg_sn, destination='toAdmin')


if __name__ == '__main__':
    set_holiday_info()
