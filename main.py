import threading
from flask_app import start_flask_app, stop_flask_app
from discord_bot import run_discord_bot, stop_discord_bot, bot
import Globals

if __name__ == '__main__':

    # Create separate threads for the Flask app, the Discord bot, and the stop handler
    flask_thread = threading.Thread(target=start_flask_app)
    discord_thread = threading.Thread(target=bot.run, args=(Globals.DAVINCI_TOKEN,))

    # Start all threads
    flask_thread.start()
    discord_thread.start()

    flask_thread.join()
    discord_thread.join()

