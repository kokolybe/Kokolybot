import ampalibe
from ampalibe import Messenger, Payload, Model, action
from ampalibe.ui import Element, Button, Type, QuickReply
from ampalibe.messenger import Filetype, Action
import json
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
        Button(type=Type.postback, title='Spotify🎶', payload=Payload('/spotify_search')),
        Button(type=Type.postback, title='YouTube🎶', payload=Payload('/youtube_search'))
    ]
    chat.persistent_menu(sender_id, persistent_menu)
    chat.send_text(sender_id, "Le menu persistant a été configuré avec succès !")

@ampalibe.command('/start')
def start(sender_id, **ext):
    chat.send_text(sender_id, "Bienvenue dans le bot ! Utilisez le menu pour explorer les options.")
# Commande principale pour gérer les messages du bot général

@ampalibe.command('/')
def main(sender_id, cmd, **ext):
    # Marquer le message de l'utilisateur comme lu
    chat.send_action(sender_id, Action.mark_seen)

    # Indiquer que le bot est en train de taper
    chat.send_action(sender_id, Action.typing_on)

    # Construire l'URL de l'API avec les paramètres appropriés
    api_url = f"https://kaiz-apis.gleeze.com/api/gemini-pro?q={cmd}&uid={sender_id}"

    try:
        # Envoyer une requête GET à l'API
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()  # Décoder la réponse JSON
            
            # Extraire le champ "response" de la réponse JSON
            bot_reply = data.get("response", "Je n'ai pas pu obtenir de réponse.")
        else:
            bot_reply = "Erreur lors de la connexion à l'API."
    except Exception as e:
        bot_reply = f"Une erreur est survenue : {e}"

    # Arrêter l'indication de "taper"
    chat.send_action(sender_id, Action.typing_off)

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
    song_url = None  # Initialiser song_url

    try:
        response = requests.get(search_url)
        if response.status_code == 200:
            data = response.json()  # Décoder la réponse JSON

            # Vérifier si la réponse est une liste et contient des chansons
            if isinstance(data, list) and data:
                song = data[0]  # Utiliser la première chanson
                song_url = song.get("trackUrl")
                title = song.get("title", "Inconnu")
                bot_reply = f"Voici le lien pour la chanson '{title}' :\n{song_url}"
            else:
                bot_reply = f"Désolé, aucun résultat trouvé pour '{cmd}'."
        else:
            bot_reply = "Erreur lors de la connexion à l'API Spotify."
    except Exception as e:
        bot_reply = f"Une erreur est survenue : {e}"

    # Répondre à l'utilisateur avec le résultat
    chat.send_text(sender_id, bot_reply)
    
    # Envoyer l'audio si song_url existe
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
    chat.send_quick_reply(sender_id, quick_rep, 'Voulez-vous chercher une autre chanson ?')

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

@ampalibe.command('/youtube_search')
def youtube_search(sender_id, **ext):
    # Demande à l'utilisateur d'entrer le titre de la recherche
    chat.send_text(sender_id, "Entrez le titre de la vidéo que vous voulez rechercher sur YouTube :")
    query.set_action(sender_id, '/youtube_results')

@ampalibe.action('/youtube_results')
def youtube_results(sender_id, cmd, **ext):
    query.set_action(sender_id, None)

    url = "https://yt-api.p.rapidapi.com/search"
    querystring = {"query": cmd}
    headers = {
        "x-rapidapi-key": "36f745d486mshd6d8e5421dd8280p1f06d0jsn7a4caec6be1c",
        "x-rapidapi-host": "yt-api.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code == 200:
            data = response.json()
            results = data.get("data", [])

            if not results:
                chat.send_text(sender_id, "Aucune vidéo trouvée pour cette recherche.")
                return

            list_items = []

            for video in results[:10]:
                try:
                    title = video.get('title', 'Titre indisponible')
                    video_id = video.get('videoId', 'ID indisponible')
                    view_count = video.get('viewCount', 'N/A')

                    thumbnail_url = None
                    if 'thumbnail' in video and isinstance(video['thumbnail'], list) and video['thumbnail']:
                        thumbnail_url = video['thumbnail'][0].get('url', 'https://via.placeholder.com/150')

                    buttons = [
                        Button(
                            type=Type.postback,
                            title="Écouter",
                            payload=Payload("/listen_video", video_id=video_id)
                        ),
                        Button(
                            type=Type.web_url,
                            title="Regarder",
                            url=f"https://www.youtube.com/watch?v={video_id}"
                        ),
                        Button(
                            type=Type.postback,
                            title="Télécharger",
                            payload=Payload("/download_video", video_id=video_id)
                        ),
                    ]

                    list_items.append(
                        Element(
                            title=f"{title} ({view_count} vues)",
                            image_url=thumbnail_url,
                            buttons=buttons,
                        )
                    )
                except Exception as e:
                    print(f"Erreur lors du traitement d'une vidéo : {e}")

            chat.send_generic_template(sender_id, list_items, next="Page suivante")
        else:
            chat.send_text(sender_id, "Erreur lors de la connexion à l'API YouTube.")
    except Exception as e:
        chat.send_text(sender_id, f"Une erreur est survenue : {e}")

@ampalibe.command('/download_video')
def download_video(sender_id, video_id, **ext):
    # URL de l'API mise à jour
    url = f"https://ytb-api-k1f7.onrender.com/download?id={video_id}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            formats = data.get("formats", [])

            # Rechercher le format correspondant à l'itag 145
            video_url = None
            for format_item in formats:
                if format_item.get("itag") == 244:
                    video_url = format_item.get("url")
                    break

            if video_url:
                chat.send_text(sender_id, "Voici le lien pour télécharger la vidéo :")
                chat.send_file_url(sender_id, video_url, filetype=Filetype.video)
            else:
                chat.send_text(sender_id, "Aucun lien vidéo correspondant à l'itag 145 n'a été trouvé.")
        else:
            chat.send_text(sender_id, f"Erreur lors de la récupération des informations vidéo. Code : {response.status_code}")
    except Exception as e:
        chat.send_text(sender_id, f"Une erreur est survenue : {e}")

@ampalibe.command('/listen_video')
def listen_video(sender_id, video_id, **ext):
    chat.send_text(sender_id, "Cette fonctionnalité sera implémentée prochainement.")

@action('/uptime_kuma')
def uptime_kuma(payload):
    # Parse les données reçues
    data = json.loads(payload)
    name = data.get('name', 'Service inconnu')
    status = data.get('status', 'N/A')
    time = data.get('time', 'N/A')
    message = data.get('message', f"🚨 Alerte : {name} est {status}.")

    # Envoie une notification au propriétaire du bot
    admin_sender_id = "100006808637969"  # Remplace par ton propre sender_id
    send(admin_sender_id, f"🔔 Notification Uptime Kuma :\n{message}\n🕒 Heure : {time}")
