import threading
from flask_app import start_flask_app
from discord_bot import run_discord_bot, bot
import Globals

if __name__ == '__main__':
    # Create separate threads for the Flask app and the Discord bot
    flask_thread = threading.Thread(target=start_flask_app)
    discord_thread = threading.Thread(target=bot.run, args=(Globals.DAVINCI_TOKEN,))

    # Start both threads
    flask_thread.start()
    discord_thread.start()

    # Wait for both threads to complete
    flask_thread.join()
    discord_thread.join()