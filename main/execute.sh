#!/bin/bash
echo '다중 파일 순차 실행해요'
{
echo '2019'
/home/ubuntu/venv_findstock/bin/python3 /home/ubuntu/project_findstock/main/00_set_holiday_info.py '2019'
echo '2020';
/home/ubuntu/venv_findstock/bin/python3 /home/ubuntu/project_findstock/main/00_set_holiday_info.py '2020'
echo '2021'
/home/ubuntu/venv_findstock/bin/python3 /home/ubuntu/project_findstock/main/00_set_holiday_info.py '2021'
echo '2022'
/home/ubuntu/venv_findstock/bin/python3 /home/ubuntu/project_findstock/main/00_set_holiday_info.py '2022'
}