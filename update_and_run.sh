#!/bin/bash
# �������� ���� � �������� �� �������� � �������� ����������� ������
CURRENT_FILE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"
# ��������� � ����
cd $CURRENT_FILE_DIR

echo "����������� �������� ��� RelaNotes. ����������, ���������.."
git pull https://digitect.visualstudio.com/Relanotes/Relanotes%20Team/_git/Relanotes
echo
echo "���������� ���������. ����������� ���������."
echo
python3 relanotes.py
echo "Press any key to exit.."
read

