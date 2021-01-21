# 일별 가격정보를 가져와서 이동평균선을 구한다.
# 지정된 이평선 정보를 지정한 일수만큼 표시 한다.
# 단 표시 기간은 최소한 지정한 이평선의 일수만큼 표시 한다.
# stc_id: 종목코드, target_ma: 이평선지정(0 인경우 전체), days: 표시기간(null 인경우 120일)
import pandas as pd
from commonModule.error_module import WrongValueError
from collectData.get_daily_price_info import get_daily_price_info

# 공통변수
MAX_MA = 240
MAX_DAYS = 240
DEFAULT_VALUE = 0


# 이동평균선 추출
def calculate_move_avg(stc_id, target_ma=DEFAULT_VALUE, days=MAX_DAYS):
    # 입력값 확인
    if target_ma not in [5, 20, 60, 120, 240, DEFAULT_VALUE]:
        raise WrongValueError(target_ma, "5, 20, 60, 120, 240, {}, None 중 하나".format(DEFAULT_VALUE))

    # 표시기간이 지정 이평선보다 작은경우 표시일자는 이평선 일자와 동일하게 설정
    if days < target_ma:
        days = target_ma

    # 표시기간이 DEFAULT_VALUE(=0)이면 MAX_DAYS(=240) 로 변경
    if days == DEFAULT_VALUE:
        days = MAX_DAYS

    # 추출 일자는 표시일자 * 2
    extract_days = days * 2

    # 결과 생성후 잘라내는 일자는 추출일자-표시일자 수
    cut_days = extract_days - days

    # 일별 가격정보 추출
    daily_info = get_daily_price_info(stc_id, extract_days).sort_values(by=['날짜'], axis=0)

    # 종가기준으로 절사단위 결정
    round_level = 0
    if daily_info['종가'].iloc[-1] < 1000:
        round_level = 0
    elif daily_info['종가'].iloc[-1] < 10000:
        round_level = -1
    elif daily_info['종가'].iloc[-1] < 100000:
        round_level = -2
    elif daily_info['종가'].iloc[-1] < 1000000:
        round_level = -3
    else:
        round_level = -4

    # 이평가격 정보 dataframe
    result_ma = pd.DataFrame()

    # 이평선 설정
    if target_ma in [5, DEFAULT_VALUE]:
        result_ma['5일이평선'] = daily_info['종가'].rolling(5).mean()
    if target_ma in [20, DEFAULT_VALUE]:
        result_ma['20일이평선'] = daily_info['종가'].rolling(20).mean()
    if target_ma in [60, DEFAULT_VALUE]:
        result_ma['60일이평선'] = daily_info['종가'].rolling(60).mean()
    if target_ma in [120, DEFAULT_VALUE]:
        result_ma['120일이평선'] = daily_info['종가'].rolling(120).mean()
    if target_ma in [240, DEFAULT_VALUE]:
        result_ma['240일이평선'] = daily_info['종가'].rolling(240).mean()

    # 결과행수
    result_cnt = result_ma.shape[0]

    # 결과 자름
    result_ma_cut = result_ma.iloc[result_cnt-cut_days:result_cnt]

    # 반올림수행
    result_ma_cut_round = round(result_ma_cut, round_level)

    # return
    return result_ma_cut_round


if __name__ == "__main__":
    print(calculate_move_avg('009460', 0, 120))
