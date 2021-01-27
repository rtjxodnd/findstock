#!/bin/bash
echo '장중 배치 수행';
{
echo '이평선 돌파종목 포착';
/home/ubuntu/venv_findstock/bin/python3 /home/ubuntu/project_findstock/main/16_msg_stc_ma_breakthrough.py >> /home/ubuntu/project_findstock/logs/16_msg_stc_ma_breakthrough.log;
}