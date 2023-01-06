# import files
from chatterbot.response_selection import get_random_response
from flask import Flask, render_template, request
from chatterbot import ChatBot, chatterbot
from chatterbot.trainers import ChatterBotCorpusTrainer
from transformers import RobertaTokenizerFast
from transformers import TFRobertaForSequenceClassification
from transformers import pipeline
import spotipy

from recommendSongsSpotify import authenticate_spotify,top_artists,top_tracks,artist_top_tracks,append_tracks_uri,select_tracks,create_playlist



mood=''
app = Flask(__name__)
username="blank"
scope='user-library-read user-read-recently-played user-top-read playlist-modify-public user-follow-read'
token=spotipy.util.prompt_for_user_token(username,scope,client_id="1c2a73de2e624a3194b30eb1ea66a45e",client_secret="3230a95c9ca349b28a88c61969156db5",redirect_uri="http://localhost:8080")


chatbot = ChatBot(
    name='Sangeeta', read_only='True', response_selection_method=get_random_response,
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.SpecificResponseAdapter'
        },
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'I honestly have no idea how to respond to that',
            'maximum_similarity_threshold': 0.85
        },
        {
            'import_path': 'chatterbot.logic.MathematicalEvaluation'
        }
    ],
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    database_uri='sqlite:///database.sqlite3'
)

trainer = ChatterBotCorpusTrainer(chatbot)
trainer.train("chatterbot.corpus.custom.chat","chatterbot.corpus.custom.annoying","chatterbot.corpus.custom.affection","chatterbot.corpus.custom.mixed","chatterbot.corpus.custom.myown","chatterbot.corpus.english")
# "chatterbot.corpus.custom.chat",
#               "chatterbot.corpus.custom.annoying",
#               "chatterbot.corpus.custom.affection",
# "chatterbot.corpus.custom.chat",
# "chatterbot.corpus.custom.annoying",
# "chatterbot.corpus.custom.affection",
# "chatterbot.corpus.custom.mixed",
# "chatterbot.corpus.custom.myown"

tokenizer = RobertaTokenizerFast.from_pretrained("arpanghoshal/EmoRoBERTa")
model = TFRobertaForSequenceClassification.from_pretrained("arpanghoshal/EmoRoBERTa")
emotion = pipeline('sentiment-analysis', model=model, tokenizer=tokenizer)

@app.route("/")
def home():
    return render_template("CHATBOT.html")

@app.route("/get")
def get_bot_response():
    global mood
    userText = request.args.get('msg')
    print(userText)
    emotion_label=emotion(userText)
    mood=emotion_label[0]['label']

    print(mood)
    print("ok")
    print(str(chatbot.get_response(userText)))



    return str(chatbot.get_response(userText))

@app.route("/",methods=['POST'])
def moodTrack():
    # if 'analyze_mood' in request.form:
    #     print("hey")
    # userText = request.args.get('msg')
    # emotion_label = emotion(userText)
    # mood = emotion_label[0]['label']
    if (mood!=''):
        print(mood)

        spotify_auth = authenticate_spotify()
        top_artists_tracks = top_artists(spotify_auth)
        top_tracks_uri = top_tracks(spotify_auth)
        artist_top_tracks_uri = artist_top_tracks(spotify_auth, top_artists_tracks)
        final_top_tracks_uri = append_tracks_uri(top_tracks_uri, artist_top_tracks_uri)
        selected_tracks = select_tracks(spotify_auth, final_top_tracks_uri, mood)
        playlist=create_playlist(spotify_auth, selected_tracks, mood)
                    # print(top_artists)
                    # print(top_tracks)
                    # print(artist_top_tracks)
                    # print(top_tracks.append(artist_top_tracks))
                    # print(final_top_tracks_uri)
        print(selected_tracks)
        print(playlist)


    return render_template('playlist.html', playlist=playlist)


if __name__ == "__main__":
    app.run()
