#!/bin/bash

cd /home/dntx/projects/Plants-Data-Telegram-Bot
git pull origin main
sudo systemctl stop plants_data_bot.service
sudo systemctl start plants_data_bot.service


