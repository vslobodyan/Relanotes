#!/usr/bin/env bash

SCRIPT_NAME="relacalc.sh"
LINK_NAME="relacalc"

SCRIPT_PATH=`pwd`
LINK_PATH="/usr/local/bin"
SCRIPT_FILENAME="$SCRIPT_PATH/$SCRIPT_NAME"
LINK_FROM="$LINK_PATH/$LINK_NAME"
LINK_TO="$SCRIPT_PATH/$SCRIPT_NAME"
echo "Создаем ссылку из $LINK_FROM на файл $LINK_TO"
sudo ln -s $LINK_TO $LINK_FROM
