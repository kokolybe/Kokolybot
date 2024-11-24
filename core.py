import ampalibe
from ampalibe import Messenger
from ampalibe import Payload
from ampalibe.ui import QuickReply

chat = Messenger()

@ampalibe.command('/')
def main(sender_id, cmd, **ext):
    chat.send_text(sender_id, "Hello, Ampalibe")
    quick_rep = [
    QuickReply(
        title="Angela",
        payload=Payload("/membre"),
        image_url="https://i.imgflip.com/6b45bi.jpg"
    ),
    QuickReply(
        title="Rivo",
        payload=Payload("/membre"),
        image_url="https://i.imgflip.com/6b45bi.jpg"
    ),
]

# next=True in parameter for displaying directly next list quick_reply
chat.send_quick_reply(sender_id, quick_rep, 'who do you choose ?') 
