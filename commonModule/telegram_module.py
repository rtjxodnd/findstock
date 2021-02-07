import telegram
from commonModule import db_module, dy_module


# 데이터세팅(종목추천)
def set_stc_data(stc_id, stc_name, text):
    data = text + "\n\n " \
            "[" + stc_name + "]\n  " \
            "https://finance.naver.com/item/main.nhn?code=" + stc_id
    print('\n송신대상: ' + stc_id + "[" + stc_name + "]")

    return data


# 데이터세팅(공지시항)
def set_notice_data():
    data = "[공지]\n" \
           "공지테스트 입니다. 여러분 새해 복 많이 받으세요" \
           "그리고 건강하세요"
    return data


# 친구에게 메시지송신(특정한 경우에는 admin 계정에게 송신)
def send_message_to_friends(data, msg_sn, destination='toGuest'):
    # db 클래스
    db_class = db_module.Database()

    # 토큰조회
    if destination == 'toGuest':
        sql = "SELECT id, token_key from findstock.cm_tokens_and_keys where key_tcd = 'telegram'"
    elif destination == 'toAdmin':
        sql = "SELECT id, token_key from findstock.cm_tokens_and_keys where key_tcd = 'telegram_admin'"
    row = db_class.execute_one(sql)

    # 토큰 및 id
    telegram_token = row['token_key']
    chat_id = row['id']
    bot = telegram.Bot(token=telegram_token)

    # 메시지 송신
    bot.sendMessage(chat_id=chat_id, text=data)

    # 메시지 송신결과 저장
    dy = dy_module.now_dy()
    tm = dy_module.now_tm()
    sn = msg_sn
    cn = data
    insert_sql = "insert into findstock.cm_sent_msg (dy, sn, tcd, tm, cn) " \
                 "values ('%s', '%s', '%s','%s', '%s')" % (dy, sn, destination, tm, cn)
    db_class.execute(insert_sql)
    db_class.commit()

    print('친구에게 메시지를 성공적으로 보냈습니다.')


if __name__ == '__main__':
    msg = set_stc_data(stc_id='005930', stc_name='삼전테스트', text='확인해봅시다.')
    msg = set_notice_data()
    send_message_to_friends(msg, 'test')
