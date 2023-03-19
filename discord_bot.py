import asyncio
import discord
import Globals
from Salai import PassPromptToSelfBot, Upscale
from image_processing import process_images, clear_images_directory
import os
from typing import Union
from discord import Message
import re
import aioredis

bot = discord.Client(intents=discord.Intents.all())

async def publish_progress_update(progress):
    redis = await aioredis.create_redis_pool("redis://localhost")
    await redis.publish("progress_update_channel", progress)
    redis.close()
    await redis.wait_closed()

# Discord bot event for when the bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# Image count variable for keeping track of the number of images processed
image_count = 0

# Discord bot event for processing received messages
@bot.event
async def on_message(message):
    global image_count

    # Ignore messages with unwanted content or from unwanted users
    if not message.content or "%" in message.content or "Waiting to start" in message.content or str(message.author.id) != Globals.MID_JOURNEY_ID:
        return

    # Save attachments from messages with "Image #" string
    if "Image #" in message.content:
        for attachment in message.attachments:
            # Create the /images directory if it doesn't exist
            if not os.path.exists("images"):
                os.makedirs("images")

            # Increment the image count
            image_count += 1

            # Save the attachment to the /images directory with the desired suffix
            file_path = os.path.join("images", f"[140,{image_count}].png")
            await attachment.save(file_path)
        return
    if message.attachments and str(message.author.id) == Globals.MID_JOURNEY_ID:
            Globals.targetID = str(message.id)
            Globals.targetHash = str((message.attachments[0].url.split("_")[-1]).split(".")[0])

            # Determine how many images to upscale based on Globals.MODE
            num_images = 4 if Globals.MODE == "Red Room" else 1

            for i in range(1, num_images + 1):
                print(f"Upscaling image {i}")
                Upscale(i, Globals.targetID, Globals.targetHash)

@bot.event
async def on_message_edit(before: Message, after: Message):
    # Ignore messages from unwanted users
    if str(after.author.id) != Globals.MID_JOURNEY_ID:
        return

    # Check if the edited message contains a progress percentage
    if "%" in after.content:
        progress = extract_progress(after.content)
        if progress is not None:
            await publish_progress_update(progress)



def extract_progress(content: str) -> Union[int, None]:
    try:
        match = re.search(r'\((\d+)%\)', content)
        if match:
            progress = int(match.group(1))
            if 0 <= progress <= 100:
                return progress
    except ValueError:
        pass
    return None


# Function to run the Discord bot and handle KeyboardInterrupt
async def run_discord_bot():
    try:
        await bot.start(Globals.DAVINCI_TOKEN)
    except KeyboardInterrupt:
        await bot.logout()

async def stop_discord_bot():
    await bot.close()


if __name__ == '__main__':
    bot.run(Globals.DAVINCI_TOKEN)