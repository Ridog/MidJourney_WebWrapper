from multiprocessing import Process
from flask_app import start_flask_app
from discord_bot import run_discord_bot, bot
import Globals

if __name__ == '__main__':
    # Create separate processes for the Flask app and the Discord bot
    flask_process = Process(target=start_flask_app)
    discord_process = Process(target=bot.run, args=(Globals.DAVINCI_TOKEN,))

    # Start both processes
    flask_process.start()
    discord_process.start()

    # Wait for both processes to complete
    flask_process.join()
    discord_process.join()