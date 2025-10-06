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
async def meme(interaction: discord.Interaction, query: str):
    # Defer the response immediately to avoid timeout
    await interaction.response.defer()

    try:
        # Call the webhook with the query and API key
        webhook_payload = {"query": query}
        headers = {"apiKey": os.getenv("API_KEY"), "Content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
            response = await client.post(
                os.getenv("WEBHOOK_URL"),
                json=webhook_payload,
                headers=headers,
                timeout=120,
            )

        if response.status_code == 200:
            # Parse JSON response to get image URL
            data = response.json()

            if data.get("success") and "data" in data:
                image_url = data["data"]["url"]
                embed = discord.Embed(title=f"Meme for: {query}", color=0x00FF00)
                embed.set_image(url=image_url)
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(
                    "Meme generation failed or returned invalid data."
                )
        else:
            await interaction.followup.send(
                f"Webhook call failed with status: {response.status_code}"
            )

    except Exception as e:
        await interaction.followup.send(f"Error calling webhook: {str(e)}")


bot.run(os.getenv("DISCORD_TOKEN"))
