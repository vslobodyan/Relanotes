@echo off
REM ���������� "���" (������ ������������� ����� �� �����).
cls
REM ������� ������
title Relanotes - update and run
REM ������ ����� ��������� ����

REM ��������� � �����, � ������� ��������� ������ � �������� ����������� �����-����.
REM ����� ������� ���� ����� �����, ���� ����.
cd /d %~dp0

echo We will update source code of RelaNotes. Please, wait..
git pull https://digitect.visualstudio.com/Relanotes/Relanotes%20Team/_git/Relanotes
echo.
echo The upgrade is complete. The program is run.
echo.
python relanotes.py
pause