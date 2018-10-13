#!/usr/bin/env bash

# Получаем путь к каталогу со скриптом и основным запускаемым файлом

##SCRIPT_LOCATION=$0
##echo "SCRIPT_LOCATION: $SCRIPT_LOCATION"
##RELANOTES_HOME=`dirname "$SCRIPT_LOCATION"`
##echo "RELANOTES_HOME: $RELANOTES_HOME"
#
##IDE_HOME=`dirname "$IDE_BIN_HOME"`
#
##RELANOTES_HOME2="$( dirname "${BASH_SOURCE[0]}" )"
##echo "RELANOTES_HOME2: $RELANOTES_HOME2"
#
##echo "1-$(dirname "$(realpath "$0")")"
##echo "2-$(dirname "$0")"
#
##CURRENT_FILE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"
##echo "CURRENT_FILE_DIR=$CURRENT_FILE_DIR"
## Переходим в него
##cd $CURRENT_FILE_DIR


#RELANOTES_HOME="$(dirname "$(realpath "$0")")"
#echo "Real path to RelaNotes is $RELANOTES_HOME"
#RELANOTES_MAIN="$RELANOTES_HOME/main.py"
#python3 "$RELANOTES_MAIN"

SCRIPT_NAME="relanotes.py"

SCRIPT_HOME="$(dirname "$(realpath "$0")")"
echo "Real path to RelaNotes is $SCRIPT_HOME"
SCRIPT_MAIN="$SCRIPT_HOME/$SCRIPT_NAME"
python3 "$SCRIPT_MAIN"


#python3 main.py
#echo "Press any key to exit.."
#read