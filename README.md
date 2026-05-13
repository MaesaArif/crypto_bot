# crypto_bot

Discord bot that gets daily crypto data.

# crontab command

CRON_TZ=Asia/Jakarta
PATH=/usr/local/sbin:/usr/local/bin:/usr/bin:/bin

0 7 * * * /home/f_devin_ahmad/crypto_bot/run_daily_price_task_7AM.sh
0 19 * * * /home/f_devin_ahmad/crypto_bot/run_daily_price_task_7PM.sh

# systemd Service (GCP VM)

To run the discord bot as a background service:

1.  **Copy the service file**:
    ```bash
    sudo cp discord_bot.service /etc/systemd/system/
    ```
2.  **Enable and start**:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable discord_bot
    sudo systemctl start discord_bot
    ```
3.  **Check logs**:
    ```bash
    sudo journalctl -u discord_bot -f
    ```
