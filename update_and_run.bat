REM ��������� � �����, � ������� ��������� ������ � �������� ����������� �����-����.
REM ����� ������� ���� ����� �����, ���� ����.
cd /d %~dp0

echo "����������� �������� ��� RelaNotes. ����������, ���������.."
git fetch https://digitect.visualstudio.com/Relanotes/Relanotes%20Team/_git/Relanotes
echo "���������� ���������. ����������� ���������."
python relanotes.py
pause