import asyncio
import aiofiles
import discord
import Globals
from Salai import PassPromptToSelfBot, Upscale
from PIL import Image
from fastapi import FastAPI, Request, WebSocket
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import time
import os
import shutil
from datetime import datetime


# Initialize FastAPI and Jinja2Templates
app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Initialize Discord bot with all intents
bot = discord.Client(intents=discord.Intents.all())

def process_images(mode: str):
    images_path = "images"
    output_filename = "Midjourney[140,0].png"
    images = [os.path.join(images_path, f) for f in os.listdir(images_path) if os.path.splitext(f)[1].lower() in ('.jpg', '.jpeg', '.png')]

    if mode == "Red Room":
        # Combine the first seven images side by side
        img_list = [Image.open(img_path) for img_path in images[:7]]
        widths, heights = zip(*(i.size for i in img_list))
        total_width = sum(widths)
        max_height = max(heights)

        new_img = Image.new('RGB', (total_width, max_height))

        x_offset = 0
        for img in img_list:
            new_img.paste(img, (x_offset, 0))
            x_offset += img.size[0]

        # Resize the combined image to 4032x1008
        resized_img = new_img.resize((4032, 1008), Image.ANTIALIAS)

    elif mode == "Manor":
        # Resize the single image to 1920x1080
        img = Image.open(images[0])
        resized_img = img.resize((1920, 1080), Image.ANTIALIAS)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    final_filename = f"Midjourney-{timestamp}[140,0].png"

    # Save the final image
    resized_img.save(os.path.join("images", final_filename))

    # Copy the final image to the watch folder
    shutil.copy(os.path.join("images", final_filename), os.path.join(Globals.WATCHFOLDER, final_filename))

    # Delete the original images
    for img_path in images:
        os.remove(img_path)

# Function to clear the images directory of files with specified extensions
def clear_images_directory(directory: str, allowed_extensions: tuple = ('.jpg', '.jpeg', '.png')):
    for file in os.listdir(directory):
        _, file_extension = os.path.splitext(file)
        if file_extension.lower() in allowed_extensions:
            os.remove(os.path.join(directory, file))

# Route for rendering the main prompt form
@app.get("/")
async def prompt(request: Request):
    return templates.TemplateResponse("prompt.html", {"request": request})

# Route for rendering the final landing page
@app.get("/final_landing")
async def final_landing(request: Request):
    return templates.TemplateResponse("final_landing.html", {"request": request})

# WebSocket endpoint for notifying the client when the expected number of images are ready
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Determine the expected number of images based on Globals.MODE
    expected_images = 8 if Globals.MODE == "Red Room" else 1

    # Poll for the expected number of images in the /images directory
    while True:
        images_count = len([f for f in os.listdir("images") if os.path.splitext(f)[1].lower() in ('.jpg', '.jpeg', '.png')])
        if images_count == expected_images:
            break
        await asyncio.sleep(1)

    # Process the images based on Globals.MODE
    process_images(Globals.MODE)

    # Notify the client when the expected number of images are detected
    await websocket.send_text("images_ready")


# Route for processing the user input and generating images
@app.post("/")
async def process_prompt(request: Request):
    clear_images_directory("images")
    form_data = await request.form()
    user_input = form_data["prompt"]
    # Append the specified string to the user's input
    user_input += Globals.PROMPT_SUFFIX

    # Determine how many times to call PassPromptToSelfBot based on Globals.MODE
    num_calls = 2 if Globals.MODE == "Red Room" else 1

    # Call PassPromptToSelfBot the required number of times
    for _ in range(num_calls):
        response = PassPromptToSelfBot(user_input)
        if response.status_code >= 400:
            print(response.text)
            print(response.status_code)
        else:
            print("Your image is being prepared, please wait a moment...")

    return templates.TemplateResponse("confirmation.html", {"request": request})

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

# Function to run the Discord bot and handle KeyboardInterrupt
async def run():
    try:
        await bot.start(Globals.DAVINCI_TOKEN)
    except KeyboardInterrupt:
        await bot.logout()

# Start the Discord bot asynchronously
asyncio.create_task(run())
