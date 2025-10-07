# Discord Bot

This is a Discord bot that runs on my Raspberry Pi 4 8GB.

## Running with Docker Compose (Recommended)

```bash
docker-compose up -d
```

To stop the bot:
```bash
docker-compose down
```

## Running with Docker

Build the Docker image:
```bash
docker build -t discord-n8n-bot .
```

Run the bot:
```bash
docker run --rm -it --env-file .env --name discord-bot -d discord-n8n-bot
```
