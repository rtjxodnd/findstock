# 이동평균선(specific_ma) 정보를 days 만큼 가져와서 해당 구간 안에서 극대극소점을 구한다.
# stc_id: 종목코드, specific_ma: 이평선특정
from scipy.signal import argrelextrema
import numpy as np
from commonModule.error_module import WrongValueError
from bizLogic.calculate_move_average import calculate_move_avg


# 극대극소 추출
def calculate_local_max_min(stc_id, specific_ma, days):
    # 입력값 확인
    if specific_ma not in [5, 20, 60, 120, 240]:
        raise WrongValueError(specific_ma, "5, 20, 60, 120, 240중 하나")

    # 이동평균선 추출
    ma_info = calculate_move_avg(stc_id, specific_ma, days)
    column = str(specific_ma)+'일이평선'
    arr_ma = np.array(ma_info[column])

    # 연속한 값중 중복한 값 제거
    arr_ma_new_unique = np.array([])
    for i, value in enumerate(arr_ma):
        if i == 0:
            arr_ma_new_unique = np.append(arr_ma_new_unique, value)
        elif arr_ma[i] != arr_ma[i-1]:
            arr_ma_new_unique = np.append(arr_ma_new_unique, value)

    # 극대값 계산
    great_index = argrelextrema(arr_ma_new_unique, np.greater)
    local_great = arr_ma_new_unique[great_index]

    # 극소값 계산
    less_index = argrelextrema(arr_ma_new_unique, np.less)
    local_less = arr_ma_new_unique[less_index]

    # 원근값
    local_old_new = np.array([])
    local_old_new = np.append(local_old_new, arr_ma_new_unique[0])
    local_old_new = np.append(local_old_new, arr_ma_new_unique[-1])

    # return
    return {'극대값': local_great, '극소값': local_less, "원근값": local_old_new}


if __name__ == "__main__":
    print(calculate_local_max_min('009460', 240, 60))
