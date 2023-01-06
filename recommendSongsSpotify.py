import random
import spotipy

username="blank"
# mood="joy"
scope='user-library-read user-read-recently-played user-top-read playlist-modify-public user-follow-read'
token=spotipy.util.prompt_for_user_token(username,scope,client_id="1c2a73de2e624a3194b30eb1ea66a45e",client_secret="3230a95c9ca349b28a88c61969156db5",redirect_uri="http://localhost:8080")


if token:

    #Step 1: Authenticating Spotipy
    def authenticate_spotify():
        print('.....Connecting to Spotify')
        # sp=spotipy.Spotify(auth_manager=token)
        sp = spotipy.Spotify(auth=token)
        # print('done')
        return sp

    # Step 2 : Creating a list of favourite artists
    def top_artists(sp):
        print('......Getting you top artists')
        top_artists_name = []
        top_artists_uri = []

        ranges = ['short_term', 'medium_term', 'long_term']
        for range in ranges:
            top_artists_all_data = sp.current_user_top_artists(limit=50, time_range=range)
            top_artists_data = top_artists_all_data['items']
            for artist_data in top_artists_data:
                if artist_data['name'] not in top_artists_name:
                    top_artists_name.append(artist_data['name'])
                    top_artists_uri.append(artist_data['uri'])

        followed_artists_all_data = sp.current_user_followed_artists(limit=50)
        followed_artists_data = (followed_artists_all_data['artists'])
        for artist_data in followed_artists_data['items']:
            if artist_data['name'] not in top_artists_name:
                top_artists_name.append(artist_data['name'])
                top_artists_uri.append(artist_data['uri'])
        return top_artists_uri

    # Step 3 : Get user's top tracks
    def top_tracks(sp):
        print("......Getting your top tracks")
        top_tracks_name = []
        top_tracks_uri = []

        ranges = ['short_term', 'medium_term', 'long_term']
        for range in ranges:
            top_tracks_all_data = sp.current_user_top_tracks(limit=50, time_range=range)
            top_tracks_data = top_tracks_all_data['items']
            for track_data in top_tracks_data:
                if track_data['name'] not in top_tracks_name:
                    top_tracks_name.append(track_data['name'])
                    top_tracks_uri.append(track_data['uri'])

        recent_tracks_all_data = sp.current_user_recently_played(limit=50)
        # print(recent_tracks_all_data['items'])
        # recent_tracks_data=recent_tracks_all_data['items']
        for idx, track_data in enumerate(recent_tracks_all_data['items']):
            track = track_data['track']
            # print(idx, track['artists'][0]['name'], " – ", track['name'])
            if track['name'] not in top_tracks_name:
                top_tracks_name.append(track['name'])
                top_tracks_uri.append(track['uri'])
            #     # top_tracks_name.append(track_data['name'])
            #     top_tracks_uri.append(track_data['uri'])

        saved_tracks_all_data = sp.current_user_saved_tracks(limit=50)
        for idx, track_data in enumerate(saved_tracks_all_data['items']):
            track = track_data['track']
            if track['name'] not in top_tracks_name:
                print(track['name'])
                top_tracks_name.append(track['name'])
                top_tracks_uri.append(track['uri'])

        return top_tracks_uri

    # Step 4 : for each artists get top traks
    def artist_top_tracks(sp, top_artists_uri):
        print(".......Getting top tracks from your favourite artists")
        top_tracks_uri = []
        for artist in top_artists_uri:
            artist_top_tracks_all_data = sp.artist_top_tracks(artist)
            artist_top_tracks_data = artist_top_tracks_all_data['tracks']
            for track_data in artist_top_tracks_data:
                top_tracks_uri.append(track_data['uri'])
                print(track_data['name'])
        return top_tracks_uri

    def append_tracks_uri(top_tracks_uri, artists_top_track_uri):
        for track_data in artists_top_track_uri:
            if track_data not in top_tracks_uri:
                top_tracks_uri.append(track_data)
        return top_tracks_uri

    # Step 5 : select tracks based on mood
    # neutral,relief: valence=
    def select_tracks(sp, top_tracks_uri, mood):
        print("......Selecting tracks")
        selected_tracks_uri = []

        def group(seq, size):
            return (seq[pos:pos + size] for pos in range(0, len(seq), size))

        random.shuffle(top_tracks_uri)
        for tracks in list(group(top_tracks_uri, 50)):
            tracks_all_data = sp.audio_features(tracks)
            for track_data in tracks_all_data:
                try:
                    if mood == "sadness" or "remorse" or "disappointment" or "embarrassment" or "grief":
                        # mood = 0.01
                        if (0 <= track_data["valence"] <= 0.35
                                and track_data["danceability"] <= 1.92
                                and track_data["energy"] <= 2.4):
                            selected_tracks_uri.append(track_data["uri"])
                    # elif 0.10 <= mood < 0.25:
                    #     if ((mood - 0.075) <= track_data["valence"] <= (mood + 0.075)
                    #             and track_data["danceability"] <= (mood * 4)
                    #             and track_data["energy"] <= (mood * 5)):
                    #         selected_tracks_uri.append(track_data["uri"])
                    elif mood == "anger" or "annoyance" or "disgust" or "disapproval" or "confusion" or "fear" or "confusion":
                        if (0.2 <= track_data["valence"] <= 0.54
                                and track_data["danceability"] <= 0.86
                                and track_data["energy"] <= 0.86):
                            selected_tracks_uri.append(track_data["uri"])
                    elif mood == "neutral" or "gratitude" or "relief" or "desire" or "curiosity" or "approval":
                        if (0.42 <= track_data["valence"] <= 0.81
                                and track_data["danceability"] >= 0.3
                                and track_data["energy"] >= 0.37):
                            selected_tracks_uri.append(track_data["uri"])
                    elif mood == "love" or "optimism" or "pride" or "caring" or "admiration":
                        if (0.67 <= track_data["valence"] <= 0.96
                                and track_data["danceability"] >= 0.45
                                and track_data["energy"] >= 0.51):
                            selected_tracks_uri.append(track_data["uri"])
                    elif mood == "joy" or "excitement" or "amusement":  # 0.75<=
                        if (0.89 <= track_data["valence"] <= 1
                                and track_data["danceability"] >= 0.57
                                and track_data["energy"] >= 0.67):
                            selected_tracks_uri.append(track_data["uri"])
                except TypeError as te:
                    continue
        return selected_tracks_uri


    # Step 6 : create playlist
    def create_playlist(sp, selected_tracks_uri, mood):
        print(".........Creating playlist")
        user_all_data = sp.current_user()
        user_id = user_all_data["id"]

        playlist_all_data = sp.user_playlist_create(user_id, "moodtracks " + mood)
        playlist_id = playlist_all_data["id"]
        playlist_uri=playlist_all_data["uri"]
        print(playlist_uri)
        random.shuffle(selected_tracks_uri)
        sp.user_playlist_add_tracks(user_id, playlist_id, selected_tracks_uri[0:40])
        print("success")
        return playlist_uri
    # spotify_auth = authenticate_spotify()
    # top_artists = top_artists(spotify_auth)
    # top_tracks=top_tracks(spotify_auth)
    # artist_top_tracks=artist_top_tracks(spotify_auth,top_artists)
    # final_top_tracks_uri=append_tracks_uri(top_tracks,artist_top_tracks)
    # selected_tracks=select_tracks(spotify_auth,final_top_tracks_uri,mood)
    # create_playlist(spotify_auth,selected_tracks,mood)
    # # print(top_artists)
    # # print(top_tracks)
    # # print(artist_top_tracks)
    # print(top_tracks.append(artist_top_tracks))
    # # print(final_top_tracks_uri)
    # print(selected_tracks)
else:
    print("could not create token")