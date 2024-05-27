
import base64
from dotenv import load_dotenv
import json
import os
from requests import post, get
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pydub import AudioSegment
from pydub.playback import play
import io







load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def main():
    print("\n\n\n\n")
    name = input("What Artist or Band do you want to Guess from: ")
    print()
    token = get_token()

    json_artist = search_artist(token, name)
    if json_artist == None:
        return False

    artist_id = json_artist["id"]
    artist_url = f"spotify:artist:{artist_id}"

    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    results = spotify.artist_top_tracks(artist_url)


    if has_preview_url(results):
        z = random.randint(0,9)
        while results["tracks"][z]['preview_url'] == None:
            z = random.randint(0,9)
    else:
        print("This Artist/Band does not have a preview for their top 10 songs")
        return False

    preview = results["tracks"][z]["preview_url"]
    if guessing_game(results, z) == True:
        print("You're Right! Congrats")
    else:
        print ("It was not this time...Maybe you should try again")


    print("name     : " + results["tracks"][z]['name'])
    print("audio    : " + results["tracks"][z]["preview_url"])
    print('cover art: ' + results["tracks"][z]['album']['images'][0]['url'])
    print()



def guessing_game(results, z):
    life = 3
    answer = 0

    guess_name = results["tracks"][z]['name']
    print("All right! Lets get this started...")
    print("You will have 3 guesses, and some hints to help you")
    print("Listen to the following audio and try to guess what the songs name:")
    play_mp3_from_url(results["tracks"][z]["preview_url"])
    print()
    print("audio    : " + results["tracks"][z]["preview_url"])


    while answer != 1 and life != 0:
        if life == 2:
            print("Wrong Answer! Try again...")
            print('cover art: ' + results["tracks"][z]['album']['images'][0]['url'])
        if life == 1:
            print("Wrong Answer! Try again...")
            print ("This song have "+str(len(guess_name.strip(" "))) + " letters")
        guess = input("What is your guess: ")
        print()
        if guess.lower() == guess_name.lower():
            answer = 1
        else:
            life -= 1

    if answer == 1:
        return True
    else:
        return False





def play_mp3_from_url(url):
     # Baixar o arquivo MP3
    response = get(url)
    with open("temp.mp3", "wb") as f:
        f.write(response.content)

    # Carregar o arquivo MP3
    song = AudioSegment.from_mp3("temp.mp3")

    # Reproduzir o arquivo MP3
    play(song)




def has_preview_url(results):

    if any(track['preview_url'] is not None for track in results['tracks']):
        return True
    else:
        return False


def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes  =  auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization" : "Basic " + auth_base64,
        "Content-Type" : "application/x-www-form-urlencoded"
    }
    data = {"grant_type":"client_credentials"}
    result = post(url, headers = headers, data = data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def build_header(token):
    return {"Authorization" : "Bearer " +  token}


def search_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    header = build_header(token)
    query = f"q={artist_name}&type=artist&limit=1&market=BR"

    query_url = url + "?" + query
    result = get (query_url, headers=header)
    json_result = json.loads(result.content)["artists"]["items"]

    if len(json_result) == 0 :
        print ("No Artists correspond to that Name")
        return None
    else:
        return json_result[0]

def songs(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=BR"
    header = build_header(token)
    result = get(url, headers= header)
    json_result = json.loads(result.content)["tracks"]
    return json_result




if __name__ == "__main__":
    main()

