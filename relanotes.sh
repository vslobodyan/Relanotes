#!/bin/bash
# �������� ���� � �������� �� �������� � �������� ����������� ������
CURRENT_FILE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"
# ��������� � ����
cd $CURRENT_FILE_DIR

python3 relanotes.py
echo "Press any key to exit.."
read