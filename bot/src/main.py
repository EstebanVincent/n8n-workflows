import os

import discord
import httpx

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)


@client.event
async def on_ready():
    print(f"Bot logged in as {client.user}")
    try:
        await tree.sync()
        print("Slash commands synced successfully.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")


@tree.command(name="meme", description="Create a meme based on your prompt")
async def meme(interaction: discord.Interaction, prompt: str):
    # Defer the response immediately to avoid timeout
    await interaction.response.defer()

    try:
        # Call the webhook with the prompt and API key
        webhook_payload = {"query": prompt}
        headers = {"apiKey": os.getenv("API_KEY"), "Content-Type": "application/json"}
        async with httpx.AsyncClient() as httpx_client:
            response = await httpx_client.post(
                os.getenv("WEBHOOK_URL"),
                json=webhook_payload,
                headers=headers,
                timeout=120,
            )

        if response.status_code == 200:
            image_url = response.json()["data"]["url"]
            embed = discord.Embed(
                title="New meme just dropped!", description=prompt, color=0x00FF00
            )
            embed.set_image(url=image_url)
            await interaction.followup.send(embed=embed)
        else:
            embed = discord.Embed(
                title=f"Webhook call failed - {response.status_code}",
                description=response.text,
                color=0xFF0000,
            )
            await interaction.followup.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="Exception",
            description=str(e),
            color=0xFF0000,
        )


client.run(os.getenv("DISCORD_TOKEN"))
