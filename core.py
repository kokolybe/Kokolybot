import ampalibe
from ampalibe import Messenger

chat = Messenger()

@ampalibe.command('/')
def main(sender_id, cmd, **ext):
    chat.send_text(sender_id, "Hello, Ampalibe")
