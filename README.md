# crypto_bot

Discord bot that gets daily crypto data.

# crontab command

CRON_TZ=Asia/Jakarta
PATH=/usr/local/sbin:/usr/local/bin:/usr/bin:/bin

0 7 _ \* _ /home/f*devin_ahmad/crypto_bot/run_daily_price_task_7AM.sh
0 19 * \* \* /home/f_devin_ahmad/crypto_botrun_daily_price_task_7PM.sh
