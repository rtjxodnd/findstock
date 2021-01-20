# https://www.data.go.kr/iim/api/selectAPIAcountView.do 에서 공휴일정보를 가져오는 소스임.
import sys
import os
import requests
import json
import xmltodict
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))
from commonModule import db_module


# 본처리
def get_holiday_info(year, month=''):
    # DB 모듈선언
    db_class = db_module.Database()

    # 키구본코드 및 서비스 id
    key_tcd = 'dataGoKr'
    service_id = 'B090041'

    # 서비스키
    sql = "SELECT token_key FROM findstock.cm_tokens_and_keys " \
          "WHERE key_tcd = '%s' AND id = '%s'" % (key_tcd, service_id)
    row = db_class.execute_one(sql)
    service_key = row['token_key']

    # 호출 url
    url = 'http://apis.data.go.kr/'+service_id+'/openapi/service/SpcdeInfoService/getRestDeInfo'

    # 입력값 설정
    query_params = '?' + 'ServiceKey=' + service_key + '&' \
                       + 'solYear=' + year + '&' + 'solMonth=' + month + '&' \
                       + 'numOfRows=100'

    # 조회 호출
    result = requests.get(url + query_params).text

    # 결과 xml 을 json 변환후 python 객체로 변환
    json_encoding = json.dumps(xmltodict.parse(result), ensure_ascii=False)
    json_decoding = json.loads(json_encoding)

    # 공휴일 추출( 조회된 공휴일이 0건 이상인 경우)
    total_count = json_decoding['response']['body']['totalCount']
    if int(total_count) > 0:
        days = json_decoding['response']['body']['items']['item']
    else:
        days = None

    # 결과내용 리턴
    return days


if __name__ == '__main__':
    print(get_holiday_info(year='2019'))
