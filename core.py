import ampalibe
from ampalibe import Messenger, Payload
from ampalibe.ui import Button, Type
import Model
import requests  # Pour envoyer une requête à l'API

chat = Messenger()
query = Model()

# Définir le menu persistant
persistent_menu = [
    Button(type=Type.postback, title='Menu', payload=Payload('/menu')),
    Button(type=Type.postback, title='Musique', payload=Payload('/spotify'))
]

# Configurer le menu persistant
@ampalibe.command('/start')
def setup_menu(sender_id, **ext):
    chat.persistent_menu(sender_id, persistent_menu)
    chat.send_text(sender_id, "Menu persistant configuré !")


# Commande principale pour gérer les messages du bot général
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


# Commande pour le bouton "Musique"
@ampalibe.command('/spotify')
def spotify(sender_id, cmd, **ext):
    chat.send_text(sender_id, "Entrez le titre de la chanson que vous voulez rechercher.")
    query.set_action(sender_id, '/get_song_title')


# Action pour rechercher une chanson
@ampalibe.action('/get_song_title')
def get_song_title(sender_id, cmd, **ext):
    # Effacer l'action courante
    query.set_action(sender_id, None)

    # Construire l'URL pour rechercher la chanson
    search_url = f"https://kaiz-apis.gleeze.com/api/spotify-search?q={cmd}"

    try:
        response = requests.get(search_url)
        if response.status_code == 200:
            data = response.json()  # Décoder la réponse JSON
            song_url = data.get("url", None)
            if song_url:
                bot_reply = f"Voici le lien pour la chanson '{cmd}' :\n{song_url}"
            else:
                bot_reply = f"Désolé, aucun résultat trouvé pour '{cmd}'."
        else:
            bot_reply = "Erreur lors de la connexion à l'API Spotify."
    except Exception as e:
        bot_reply = f"Une erreur est survenue : {e}"

    # Répondre à l'utilisateur avec le résultat
    chat.send_text(sender_id, bot_reply)
