import ampalibe
from ampalibe import Messenger
from ampalibe import Payload
from ampalibe.ui import QuickReply

chat = Messenger()

@ampalibe.command('/')
def main(sender_id, cmd, **ext):
    # Envoyer un message texte
    chat.send_text(sender_id, "Hello, Ampalibe")
    
    # Créer des quick replies
    quick_rep = [
        QuickReply(
            title="Angela",
            payload=Payload("/membre"),
            image_url="https://i.imgflip.com/6b45bi.jpg"
        ),
        QuickReply(
            title="kouly",
            payload=Payload("/membre"),
            image_url="https://i.imgflip.com/6b45bi.jpg"
        ),
    ]

    # Envoyer les quick replies
    chat.send_quick_reply(sender_id, quick_rep, 'Who do you choose?')
