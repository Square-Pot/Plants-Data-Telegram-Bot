#!/bin/bash

cd /home/dntx/projects/Plants-Data-Telegram-Bot
git pull origin main
sudo /bin/systemctl restart plants_data_bot.service


