import io
import os

import discord
import httpx
from discord.ext import commands

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Bot logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)


@bot.tree.command(name="meme", description="Send a random meme")
async def meme(
    interaction: discord.Interaction, query: str = "meme on bitcoin all time high today"
):
    try:
        # Call the webhook with the query and API key
        webhook_payload = {"query": query}
        headers = {"apiKey": os.getenv("API_KEY"), "Content-Type": "application/json"}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                os.getenv("WEBHOOK_URL"), json=webhook_payload, headers=headers
            )

        if response.status_code == 200:
            # Create a Discord file from the binary image data
            image_buffer = io.BytesIO(response.content)
            image_file = discord.File(fp=image_buffer, filename="meme.png")
            await interaction.response.send_message(
                content=f"Here's your meme for: {query}", file=image_file
            )
        else:
            await interaction.response.send_message(
                f"Webhook call failed with status: {response.status_code}"
            )

    except Exception as e:
        await interaction.response.send_message(f"Error calling webhook: {str(e)}")


bot.run(os.getenv("DISCORD_TOKEN"))
