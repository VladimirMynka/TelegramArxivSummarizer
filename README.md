# Monitor articles from arXiv

#### Installation

1. Install python and poetry:

```bash
pip install poetry==1.8.4
```

2. Install dependencies:

```bash
poetry install
```

3. Set environment variables:

In Linux:
```bash
export TELEGRAM_BOT_TOKEN = '<Your Telegram bot token>';
export OPENAI_API_KEY = '<Your OpenAI API token>';
export OPENAI_URL = '<Your OpenAI URL, for example https://api.vsegpt.ru/v1>';
export CHANNEL_ID = '<Your Telegram channel ID>';
export SEARCH_QUERY = '<Query to search articles, for example "Diffusion text generation">';
export CHECK_INTERVAL = <Check interval in seconds, for example 600>;
```

In Windows:
```bash
set TELEGRAM_BOT_TOKEN = '<Your Telegram bot token>';
set OPENAI_API_KEY = '<Your OpenAI API token>';
set OPENAI_URL = '<Your OpenAI URL, for example https://api.vsegpt.ru/v1>';
set CHANNEL_ID = '<Your Telegram channel ID>';
set SEARCH_QUERY = '<Query to search articles, for example "Diffusion text generation">';
set CHECK_INTERVAL = <Check interval in seconds, for example 600>;
```

4. Run the bot:

```bash
python -m src.arxiv_monitor
```


#### Telegram bot creation
To create a telegram bot, you need to talk to [BotFather](https://t.me/botfather) and follow these steps:
1. `/newbot`
2. Enter the name of the bot
3. Enter the username of the bot, it must end with `bot`
4. Copy the token and save it, it will be used to set the `TELEGRAM_BOT_TOKEN` environment variable


#### Telegram channel creation
To create a telegram channel, you need to follow these steps:
1. Search for the channel in the telegram app
2. Open the channel in the browser
3. Copy the channel ID from the URL, it will be used to set the `CHANNEL_ID` environment variable
4. Add the bot to the channel as an administrator and give it the necessary permissions
