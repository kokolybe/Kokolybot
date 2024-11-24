import ampalibe
from ampalibe import Messenger
import requests  # Pour envoyer une requête à l'API

chat = Messenger()

# Commande principale pour gérer les messages entrants
@ampalibe.command('/')
def main(sender_id, cmd, **ext):

    # Construire l'URL de l'API avec le message de l'utilisateur
    api_url = f"https://kaiz-apis.gleeze.com/api/gpt-4o?q={cmd}&uid={sender_id}"

    # Envoyer une requête GET à l'API
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()  # Décoder la réponse JSON
            bot_reply = data.get("response", "Désolé, je n'ai pas pu obtenir de réponse.")
        else:
            bot_reply = "Erreur lors de la connexion à l'API."
    except Exception as e:
        bot_reply = f"Une erreur est survenue : {e}"

    # Répondre à l'utilisateur
    chat.send_text(sender_id, bot_reply)
