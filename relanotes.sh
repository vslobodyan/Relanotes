#!/bin/bash
# Получаем путь к каталогу со скриптом и основным запускаемым файлом
CURRENT_FILE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"
# Переходим в него
cd $CURRENT_FILE_DIR

python3 relanotes.py
echo "Press any key to exit.."
read