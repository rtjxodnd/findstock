#!/bin/bash
echo '연말 배치 수행';
{
echo '휴일정보 수신';
/home/ubuntu/venv_findstock/bin/python3 /home/ubuntu/project_findstock/main/00_set_holiday_info.py > /home/ubuntu/project_findstock/logs/00_set_holiday_info.log;
}