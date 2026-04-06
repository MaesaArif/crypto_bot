# Running a Discord Bot on GCP Compute Engine with systemd

This guide covers how to set up your Discord bot as a `systemd` service on a GCP Compute Engine instance so it automatically starts on boot and restarts on crash.

---

## Prerequisites

- A GCP Compute Engine instance (Ubuntu/Debian recommended)
- Python 3 installed on the instance
- Your Discord bot files uploaded to the instance
- SSH access to the instance

---

## 1. Prepare Your Bot

SSH into your instance and navigate to your bot's directory.

### Create a virtual environment

```bash
python3 -m venv venv
source venv/activate
pip install -r requirements.txt
```

### Set up your `.env` file

```bash
nano /path/to/your/bot/.env
```

Add your secrets:

```env
DISCORD_TOKEN=your_token_here
PREFIX=!
```

Lock down file permissions:

```bash
chmod 600 /path/to/your/bot/.env
```

---

## 2. Create the systemd Service File

```bash
sudo nano /etc/systemd/system/discord-bot.service
```

Paste the following, replacing the placeholders with your actual values:

```ini
[Unit]
Description=Discord Bot
After=network.target

[Service]
User=your_username
WorkingDirectory=/path/to/your/bot
EnvironmentFile=/path/to/your/bot/.env
ExecStart=/path/to/your/bot/venv/bin/python3 /path/to/your/bot/bot.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Key fields explained

| Field | Description |
|---|---|
| `User` | The Linux user that runs the bot process |
| `WorkingDirectory` | Root directory of your bot project |
| `EnvironmentFile` | Path to your `.env` file |
| `ExecStart` | Path to Python in your venv + your bot script |
| `Restart=always` | Automatically restarts the bot if it crashes |
| `RestartSec=5` | Waits 5 seconds before restarting |

---

## 3. Enable and Start the Service

Reload systemd to register the new service:

```bash
sudo systemctl daemon-reload
```

Enable it to auto-start on boot:

```bash
sudo systemctl enable discord-bot
```

Start the service:

```bash
sudo systemctl start discord-bot
```

---

## 4. Verify It's Running

```bash
sudo systemctl status discord-bot
```

You should see `Active: active (running)` in the output.

---

## 5. Viewing Logs

Stream live logs:

```bash
sudo journalctl -u discord-bot -f
```

View the last 50 lines:

```bash
sudo journalctl -u discord-bot -n 50
```

View logs from the current boot only:

```bash
sudo journalctl -u discord-bot -b
```

---

## 6. Managing the Service

| Command | Description |
|---|---|
| `sudo systemctl start discord-bot` | Start the bot |
| `sudo systemctl stop discord-bot` | Stop the bot |
| `sudo systemctl restart discord-bot` | Restart the bot |
| `sudo systemctl status discord-bot` | Check current status |
| `sudo systemctl disable discord-bot` | Disable auto-start on boot |

> After making any changes to the `.service` file, always run `sudo systemctl daemon-reload` followed by `sudo systemctl restart discord-bot`.

---

## Troubleshooting

**Bot crashes immediately on start**
- Check logs with `journalctl -u discord-bot -n 50`
- Verify your `DISCORD_TOKEN` in `.env` is correct
- Make sure the `ExecStart` path to Python and `bot.py` are correct

**EnvironmentFile not found error**
- Double-check the path in `EnvironmentFile=` matches where your `.env` file actually is

**Permission denied errors**
- Ensure the `User=` in the service file owns the bot directory and `.env` file
  ```bash
  sudo chown -R your_username:your_username /path/to/your/bot
  ```

**Changes to bot code not reflected**
- Always restart the service after updating your code:
  ```bash
  sudo systemctl restart discord-bot
  ```
