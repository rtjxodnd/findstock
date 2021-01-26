import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
from commonModule import db_module, dy_module
from collectData.get_detail_info import get_detail_info
from bizLogic.calculate_move_average import calculate_move_avg
from bizLogic.analysis_ma_chart import analysis_ma_chart
from commonModule.telegram_module import set_stc_data, send_message_to_friends


# DB insert
def insert_stc_alarm(db_class, dy, stc_id, price, msg_sn):
    # DB Insert
    try:
        sql = "INSERT INTO findstock.sc_stc_alarm (dy, alarm_sn, stc_id, judge_tcd, price, msg_sn) " \
              "VALUES ('%s', (select ifnull(max(x.alarm_sn),0)+1 from findstock.sc_stc_alarm x where dy='%s'), " \
              "'%s', '%s', '%d', '%s')" % (dy, dy, stc_id, 'maBreakthrough', price, msg_sn)
        db_class.execute(sql)
        db_class.commit()
        return
    except Exception as de:
        print("에러: 이평선 돌파 종목 판별/알림 정보 입력시 에러. 일자: {}, 종목코드: {}, 가격: {}".format(dy, stc_id, price))
        print(de)


# 이평선 돌파 판단
def judge_ma_breakthrough(ma_num, compare_ma, ma_data):
    # 비교하는 기준 이평선 가격추출: (ma==1 의경우는 현재 가격을 의미 한다.)
    base_ma_list = ma_data[ma_data['ma'] == ma_num]
    base_price_old = base_ma_list['old'].iloc[0]
    base_price_new = base_ma_list['new'].iloc[0]

    # 비교하는 대상 이동평균 값만 추출: ma_num 보다 크면서 compare_ma에 포함되는 이평선
    ma_list = ma_data[ma_data['ma'] > ma_num]
    compare_ma_list = ma_list[ma_list['ma'].isin(compare_ma)]

    # 중간값 초기화
    middle_msg = ''
    break_yn = False

    # 이평선 돌파여부 확인
    for i in range(compare_ma_list.shape[0]):
        # 이평선 이름
        ma_name = str(compare_ma_list['ma'].iloc[i])

        # 비교대상 이평선
        ma_old = compare_ma_list['old'].iloc[i]
        ma_new = compare_ma_list['new'].iloc[i]

        # 상위 이평선 돌파 판정
        if base_price_old <= ma_old and base_price_new > ma_new:
            middle_msg = middle_msg + ma_name + " "
            break_yn = True

        # 메시지 조립
        if break_yn:
            if ma_num == 1:
                middle_msg = "현재가: " + middle_msg + "일선 돌파! \n"
            else:
                middle_msg = str(ma_num) + "일선: " + middle_msg + "일선 돌파! \n"

        return {"break_yn": break_yn, "middle_msg": middle_msg}


# 이평선 돌파시 메시지 송신
def get_ma_and_send_message(check_ma, compare_ma, in_stc_id=None):
    # db 모듈
    db_class = db_module.Database()

    # 당일
    dy = dy_module.now_dy()

    # 대상건 조회
    sql = "select a.stc_id, b.stc_name, b.price, a.ma5, a.ma20, a.ma60, a.ma120, a.ma240 " \
          "from findstock.sc_stc_move_avg a, findstock.sc_stc_basic b, findstock.sc_stc_filter c " \
          "where a.stc_id = b.stc_id and a.stc_id = c.stc_id and c.helth_yn = 'Y' and b.tot_value > 500000000000"

    if in_stc_id is not None:
        sql = "select a.stc_id, b.stc_name, b.price, a.ma5, a.ma20, a.ma60, a.ma120, a.ma240 " \
              "from findstock.sc_stc_move_avg a, findstock.sc_stc_basic b " \
              "where a.stc_id = b.stc_id and a.stc_id = '%s'" % in_stc_id

    rows = db_class.execute_all(sql)

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
            new_now_price = get_detail_info(stc_id)['가격정보']['현재가'].iloc[0]
            new_ma5 = price_info['5일이평선']
            new_ma20 = price_info['20일이평선']
            new_ma60 = price_info['60일이평선']
            new_ma120 = price_info['120일이평선']
            new_ma240 = price_info['240일이평선']

            # 새로운 값 DB저장(이평선 정보)
            sql = "update findstock.sc_stc_move_avg " \
                  "set ma5 = '%d', ma20 = '%d', ma60= '%d', ma120 = '%d', ma240 = '%d'" \
                  "where stc_id = '%s'" % (new_ma5, new_ma20, new_ma60, new_ma120, new_ma240, stc_id)
            db_class.execute(sql)

            # 새로운 값 DB저장(현재가 정보)
            sql = "update findstock.sc_stc_basic " \
                  "set price = '%d' where stc_id = '%s'" % (new_now_price, stc_id)
            db_class.execute(sql)
            db_class.commit()

            # 이평선 돌파 확인 위한 dataframe
            ma_data_list = {'ma': [1, 5, 20, 60, 120, 240],
                            'old': [old_now_price, old_ma5, old_ma20, old_ma60, old_ma120, old_ma240],
                            'new': [new_now_price, new_ma5, new_ma20, new_ma60, new_ma120, new_ma240]}

            ma_data = pd.DataFrame(ma_data_list)

            # 이평선 돌파여부 확인
            result_now = {"break_yn": False, "middle_msg": ''}
            result_5 = {"break_yn": False, "middle_msg": ''}
            result_20 = {"break_yn": False, "middle_msg": ''}
            result_60 = {"break_yn": False, "middle_msg": ''}
            result_120 = {"break_yn": False, "middle_msg": ''}

            if 1 in check_ma:
                result_now = judge_ma_breakthrough(1, compare_ma, ma_data)
            if 5 in check_ma:
                result_5 = judge_ma_breakthrough(5, compare_ma, ma_data)
            if 20 in check_ma:
                result_20 = judge_ma_breakthrough(20, compare_ma, ma_data)
            if 60 in check_ma:
                result_60 = judge_ma_breakthrough(60, compare_ma, ma_data)
            if 120 in check_ma:
                result_120 = judge_ma_breakthrough(120, compare_ma, ma_data)

            # 돌파여부
            yn_now = result_now['break_yn']
            yn_5 = result_5['break_yn']
            yn_20 = result_20['break_yn']
            yn_60 = result_60['break_yn']
            yn_120 = result_120['break_yn']

            # 메시지조합
            msg_now = result_now['middle_msg']
            msg_5 = result_5['middle_msg']
            msg_20 = result_20['middle_msg']
            msg_60 = result_60['middle_msg']
            msg_120 = result_120['middle_msg']

            # 최종 메시지 조립
            msg_final = msg_now + msg_5 + msg_20 + msg_60 + msg_120

            # 이평선 돌파 조건 충족시
            yn_ma = False
            if yn_now or yn_5 or yn_20 or yn_60 or yn_120:
                yn_ma = True

            # 이평선 돌파 조건 충족시 5일선과 종가 이격도 체크
            yn_diff_ma_05 = False
            if yn_ma:
                ma05_analysis = analysis_ma_chart(stc_id, 5, 5)
                ma05_last = ma05_analysis["local_max_min_info"]["원근값"][1]
                if new_now_price / ma05_last < 1.05:
                    yn_diff_ma_05 = True

            # 메시지 송신
            if yn_ma and yn_diff_ma_05:
                # 메시지순번(시간값으로 대신함)
                msg_sn = dy_module.now_dt("%Y%m%d%H%M%S%f")

                # 메시지송신
                msg = set_stc_data(stc_id=stc_id, stc_name=stc_name, text=msg_final)
                send_message_to_friends(msg, msg_sn)

                # db insert
                insert_stc_alarm(db_class, dy, stc_id, new_now_price, msg_sn)

        except Exception as ex:
            print("에러: 이평선 돌파 값 저장 및 메시지 송신 에러. 종목코드: {}".format(stc_id))
            print(ex)

    db_class.commit()

    return


def msg_stc_ma_breakthrough(check_ma=None, compare_ma=None, in_stc_id=None):
    # default 값 설정
    if check_ma is None:
        check_ma = [1, 5, 20, 60, 120]
    if compare_ma is None:
        compare_ma = [5, 20, 60, 120]

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
    get_ma_and_send_message(check_ma, compare_ma, in_stc_id)

    # 종료 시간
    end_time = dy_module.now_dt("%Y-%m-%d %H:%M:%S")

    # 종료메시지
    end_msg = "이평선 돌파 메시지 송신 종료!!!\n" + \
              "시작시각: {}\n".format(start_time) + \
              "종료시각: {}\n".format(end_time)
    print(end_msg)

    # 종료메시지송신
    end_msg_sn = dy_module.now_dt("%Y%m%d%H%M%S%f")
    send_message_to_friends(data=end_msg, msg_sn=end_msg_sn, destination='admin')


if __name__ == "__main__":
    msg_stc_ma_breakthrough([20], [120], )
