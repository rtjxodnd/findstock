# 재무적으로 우수한 종목을 선별해 낸다.
# 52주 최저가의 2배가 현재가 보다 커야 함
# 최근 3년 매출액이 모두 양수여야 함
# 최근 영업이익이 모두 양수여야 함
# 당기순이익 평균이 0보다 커야 함
# 부채비율이 150보다 작아야 함
# 유보율이 100보다 커야 함
# 마지막분기 매출액이 양수여야 함
# 마지막분기 영업이익이 양수여야 함
# 3년이내 일거래금액이 100억 이상인 경우가 존재해야 함
import pandas as pd
from collectData.get_detail_info import get_detail_info
from collectData.get_daily_price_info import get_daily_price_info


def filter_good_condition(stc_id):
    try:
        # 종목 상세 정보 get
        stc_detail_info = get_detail_info(stc_id)

        # 가격정보
        df_price_info = pd.DataFrame(stc_detail_info['가격정보'])

        # 년재무정보(3개년추출)
        df_finance_year = pd.DataFrame(stc_detail_info['년재무정보'])
        extract_point = df_finance_year.shape[0] - 3
        if extract_point < 0:
            extract_point = 0
        df_finance_year = df_finance_year.iloc[extract_point:]

        # 분기재무정보(3개분기추출)
        df_finance_quarter = pd.DataFrame(stc_detail_info['분기재무정보'])
        extract_point = df_finance_quarter.shape[0] - 3
        if extract_point < 0:
            extract_point = 0
        df_finance_quarter = df_finance_quarter.iloc[extract_point:]

        # 연간 재무정보 없으면 false return
        if df_finance_year.shape[0] == 0:
            return False

        # 52주 최저가의 2배가 현재가 보다 작으면 매수 안함
        if float(df_price_info['52최저가']) * 2 < float(df_price_info['현재가']):
            return False

        # 최근 3년 매출액 중 음수가 있으면 매수 안함
        if df_finance_year[df_finance_year['매출액'] < 0].shape[0] > 0:
            return False

        # 최근 영업이익 중 음수가 있으면 매수 안함
        if df_finance_year[df_finance_year['영업이익'] < 0].shape[0] > 0:
            return False

        # 당기순이익 평균이 0보다 작으면 매수 안함
        if df_finance_year['당기순이익'].mean() < 0:
            return False

        # 부채비율이 150보다 크면 매수 안함
        if df_finance_year['부채비율'].mean() > 150:
            return False

        # 유보율이 100보다 작으면 매수 안함
        if df_finance_year['유보율'].mean() < 100:
            return False

        # 분기 재무정보 있는 경우만 이후 확인
        if df_finance_quarter.shape[0] > 0:

            # 마지막분기 매출액 음수인 경우
            if df_finance_quarter['매출액'].iloc[-1] < 0:
                return False

            # 마지막분기 영업이익 음수인 경우
            if df_finance_quarter['영업이익'].iloc[-1] < 0:
                return False

        # 3년이내 일거래 100억 존재 안하면 매수 안함
        # 종목 일별 정보 get
        stc_daily_info = get_daily_price_info(stc_id, 720)
        stc_daily_info['거래금액'] = stc_daily_info['종가']*stc_daily_info['거래량']
        if stc_daily_info[stc_daily_info['거래금액'] > 10000000000].shape[0] < 1:
            return False

    except Exception as e:
        print("에러: 상세정보 추출시 에러. 종목코드: {}".format(stc_id))
        print(e)
        return False

    # 끝까지 모든 조건 충족시 True 리턴
    return True


if __name__ == '__main__':
    print(filter_good_condition('352820')) # 352820
