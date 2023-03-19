import os
import shutil
from datetime import datetime
from PIL import Image
import Globals

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