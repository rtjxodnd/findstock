# 이동평균선(specific_ma) 정보를 days 만큼 가져와서 해당 구간 안에서 극대극소점을 구한다.
# stc_id: 종목코드, specific_ma: 이평선특정, days: 추출일수
# 이평선 추세를 9가지로 나눈다 극대점 [상승/횡보/하락] X 극소점 [상승/횡보/하락]
# 상승/횡보/하락: 1/0/-1로 표기함.
import numpy as np
from commonModule.error_module import WrongValueError
from bizLogic.calculate_local_max_min import calculate_local_max_min

# 공통변수(상승/하락/횡보 기준)
UP_BASE = 0.05
DN_BASE = -0.05


# 이평선 차트분석
def analysis_ma_chart(stc_id, specific_ma, days):
    # 입력값 확인
    if specific_ma not in [5, 20, 60, 120]:
        raise WrongValueError(specific_ma, "5, 20, 60, 120중 하나")

    # 극대극소 추출
    local_max_min_info = calculate_local_max_min(stc_id, specific_ma, days)

    # 극대값 분석
    if np.size(local_max_min_info['극대값']) < 2:
        local_max_gradient = np.gradient(local_max_min_info['원근값']).mean()/local_max_min_info['원근값'][0]
    else:
        local_max_gradient = np.gradient(local_max_min_info['극대값']).mean() / local_max_min_info['극대값'][0]

    # 극대값 판별
    if local_max_gradient > UP_BASE:
        high_trend = 1
    elif local_max_gradient < DN_BASE:
        high_trend = -1
    else:
        high_trend = 0

    # 극소값 분석
    if np.size(local_max_min_info['극소값']) < 2:
        local_min_gradient = np.gradient(local_max_min_info['원근값']).mean()/local_max_min_info['원근값'][0]
    else:
        local_min_gradient = np.gradient(local_max_min_info['극소값']).mean() / local_max_min_info['극소값'][0]

    # 극소값 판별
    if local_min_gradient > UP_BASE:
        low_trend = 1
    elif local_min_gradient < DN_BASE:
        low_trend = -1
    else:
        low_trend = 0

    # return
    return {"high_trend": high_trend, "low_trend": low_trend, "local_max_min_info": local_max_min_info}


if __name__ == "__main__":
    print(analysis_ma_chart('034730', 5, 60))#009460
    # print(np.gradient([1,3,9]).mean())
