# Future Planfix Bot

Future Planfix Bot - асинхронный телеграмм бот на Python, помогающий отслеживать чек-листы из задач веб-сервиса PlanFix. Приложение спроектировано и сконструировано в рамках прохождения технической практики студентов МГТУ им. Н.Э Баумана.

## Setup
### .env contains
```bash
BOT_TOKEN=...  # from BotFather
BOT_TYPE=[POLLING|WEBHOOK]  # bot mode
WEBHOOK_URL=...  # your bot domain - only for WEBHOOK
WEBHOOK_PORT=...  # your bot port - only for WEBHOOK
DB_URL=...  # postgres db url
DB_HOST=...  # postgres db host
DB_NAME=...  # postgres db name
DB_USER=...  # postgres db user
DB_PASSWORD=...  # postgres db password
ENDPOINT=...  # where api gets info - https://***.planfix.ru
OWNER_IDS=<id1>,<id2>,...  # admins telegram ids separated by comma
```
### secret.py contains
cookies, headers - dictionary from your administration session
data dictionary contains 'get_check_list' with command for getting checkList from the page and create_task dictionary with data for creating task
```python
cookies = {...}
headers = {...}
data = {
    'get_check_list': '...',
    'create_task': {...}
}
```


### Linux:
```bash
sudo docker build -f Dockerfile -t bot . && sudo docker run --privileged -p 0.0.0.0:228:228 -it bot
```
