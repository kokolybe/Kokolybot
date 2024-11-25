import ampalibe
from ampalibe import Messenger, Payload, Model
from ampalibe.ui import Element, Button, Type, QuickReply
from ampalibe.messenger import Filetype, Action
import requests  # Pour envoyer une requête à l'API

chat = Messenger()
query = Model()

@ampalibe.command('/setup')
def setup(sender_id, **ext):
    # Étape 1 : Configurer le bouton "Get Started"
    chat.get_started(payload="/start")
    chat.send_text(sender_id, "Le bouton 'Get Started' a été configuré avec succès !")

    # Étape 2 : Configurer le menu persistant
    persistent_menu = [
        Button(type=Type.postback, title='Menu', payload=Payload('/menu')),
        Button(type=Type.postback, title='Musique', payload=Payload('/spotify')),
        Button(type=Type.postback, title='Spotify🎶', payload=Payload('/spotify_search'))
    ]
    chat.persistent_menu(sender_id, persistent_menu)
    chat.send_text(sender_id, "Le menu persistant a été configuré avec succès !")

@ampalibe.command('/start')
def start(sender_id, **ext):
    chat.send_text(sender_id, "Bienvenue dans le bot ! Utilisez le menu pour explorer les options.")
# Commande principale pour gérer les messages du bot général

@ampalibe.command('/')
def main(sender_id, cmd, **ext):
    # Construire l'URL de l'API avec les paramètres appropriés
    api_url = f"https://joshweb.click/api/gpt-4o?q={cmd}&uid={sender_id}"

    try:
        # Envoyer une requête GET à l'API
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()  # Décoder la réponse JSON
            if data.get("status"):
                # Utiliser le champ "result" pour répondre
                bot_reply = data.get("result", "Je n'ai pas pu obtenir de réponse.")
            else:
                bot_reply = "L'API a retourné une réponse invalide."
        else:
            bot_reply = "Erreur lors de la connexion à l'API."
    except Exception as e:
        bot_reply = f"Une erreur est survenue : {e}"

    # Répondre à l'utilisateur
    chat.send_action(sender_id, Action.mark_seen)
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
    
    # Envoyer l'audio
    if song_url:
        chat.send_file_url(sender_id, song_url, filetype=Filetype.audio)
    
    # Ajouter les Quick Replies pour une nouvelle recherche
    quick_rep = [
        QuickReply(
            title="Oui",
            payload=Payload("/spotify"),
            image_url="https://i.pinimg.com/236x/2b/1d/e7/2b1de7265af232b446a0de943eb47b43.jpg"
        ),
        QuickReply(
            title="Non",
            payload=Payload("/menu"),
            image_url="https://i.pinimg.com/736x/0e/09/b3/0e09b3871254565400df91d6a90e6c33.jpg"
        ),
    ]

    # Afficher les Quick Replies à l'utilisateur
    chat.send_quick_reply(sender_id, 'Voulez-vous chercher une autre chanson ?', quick_rep)

# Commande pour demander le titre de la chanson
@ampalibe.command('/spotify_search')
def spotify_search(sender_id, **ext):
    chat.send_text(sender_id, "Entrez le titre de la chanson que vous voulez rechercher.")
    query.set_action(sender_id, '/spotify_results')  # Enregistre l'action suivante

# Action pour rechercher la chanson
@ampalibe.action('/spotify_results')
def get_song_title(sender_id, cmd, **ext):
    # Effacer l'action courante
    query.set_action(sender_id, None)

    # URL de recherche
    search_url = f"https://joshweb.click/search/spotify?q={cmd}"

    try:
        response = requests.get(search_url)
        if response.status_code == 200:
            data = response.json()
            results = data.get("result", [])

            # Vérifier s'il y a des résultats
            if not results:
                chat.send_text(sender_id, "Aucun résultat trouvé pour cette recherche.")
                return

            # Créer la liste des éléments pour le générique template
            list_items = []

            for song in results:
                # Boutons pour chaque chanson
                buttons = [
                    Button(
                        type=Type.postback,
                        title="Écouter",
                        payload=Payload(
                            "/musique_download",
                            url=song['direct_url'],
                            title=song['title'],
                            artist=song['artist']
                        ),
                    ),
                    Button(
                        type=Type.web_url,
                        title="Voir sur Spotify",
                        url=song['url'],
                    ),
                ]

                # Ajouter un élément au générique template
                list_items.append(
                    Element(
                        title=f"{song['title']} - {song['artist']}",
                        image_url="https://i.imgur.com/6b45bi.jpg",  # Placeholder pour l'image
                        buttons=buttons,
                    )
                )

            # Envoyer le générique template avec pagination
            chat.send_generic_template(sender_id, list_items, next="Page suivante")
        else:
            chat.send_text(sender_id, "Erreur lors de la connexion à l'API Spotify.")
    except Exception as e:
        chat.send_text(sender_id, f"Une erreur est survenue : {e}")

@ampalibe.command('/musique_download')
def musique_download(sender_id, url, title, artist, **ext):
    try:
        # Vérifier si l'URL directe existe
        if not url:
            chat.send_text(sender_id, "Lien de téléchargement indisponible pour cette chanson.")
            return

        # Télécharger le fichier audio
        response = requests.get(url)
        if response.status_code == 200:
            # Renommer et enregistrer le fichier
            filename = f"{title} - {artist}.mp3"
            filepath = f"/tmp/{filename}"

            with open(filepath, "wb") as file:
                file.write(response.content)

            # Envoyer le fichier à l'utilisateur
            chat.send_file(sender_id, filepath)
        else:
            chat.send_text(sender_id, "Erreur lors du téléchargement de la musique.")
    except Exception as e:
        chat.send_text(sender_id, f"Une erreur est survenue : {e}")
