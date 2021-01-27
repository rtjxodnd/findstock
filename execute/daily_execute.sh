#!/bin/bash
echo '일배치 수행';
{
echo '종목기본 수신';
/home/ubuntu/venv_findstock/bin/python3 /home/ubuntu/project_findstock/main/10_set_stc_basic_info.py > /home/ubuntu/project_findstock/logs/10_set_stc_basic_info.log;
echo '매집봉 체크';
/home/ubuntu/venv_findstock/bin/python3 /home/ubuntu/project_findstock/main/12_set_buying_candle.py > /home/ubuntu/project_findstock/logs/12_set_buying_candle.log;
echo '매집봉 유효성 업데이트';
/home/ubuntu/venv_findstock/bin/python3 /home/ubuntu/project_findstock/main/13_chk_buying_candle.py > /home/ubuntu/project_findstock/logs/13_chk_buying_candle.log;
echo '급등가능종목 추출 및 메시지 송신';
/home/ubuntu/venv_findstock/bin/python3 /home/ubuntu/project_findstock/main/14_msg_stc_possible_to_go.py > /home/ubuntu/project_findstock/logs/14_msg_stc_possible_to_go.log;
echo '재무 우수종목 이평선 설정';
/home/ubuntu/venv_findstock/bin/python3 /home/ubuntu/project_findstock/main/15_set_stc_move_average.py other_day > /home/ubuntu/project_findstock/logs/15_set_stc_move_average.log;
}