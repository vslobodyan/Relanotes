
REM ������ ����� ��������� ������ ������.
REM �� ��� �������� � ���� ����� � �������� ������ ����.

REM �����, �� ������� ��������� ������
REM @echo cd = %cd%

REM �����, � ������� ��������� ������
REM @echo dp0 = %~dp0

REM ��������� � �����, � ������� ��������� ������ � �������� ����������� �����-����.
REM ����� ������� ���� ����� �����, ���� ����.
cd /d %~dp0
REM ��������� �������� ����������� ����
python relanotes.py
REM c:\python35\python.exe D:\Dropbox\Projects\Relanotes\Relanotes-qt5-0.03\relanotes.py
pause
