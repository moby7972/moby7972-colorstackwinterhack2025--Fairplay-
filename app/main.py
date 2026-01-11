from dotenv import load_dotenv
load_dotenv()

from collections import Counter
import urllib.parse


from fastapi import FastAPI
from app.spotify import router as spotify_router, spotify_get
from app.analysis import analyze, recommend

app = FastAPI(title="FairPlay")
app.include_router(spotify_router)


@app.get("/")
def root():
    return {"status": "ok", "message": "FairPlay API is running"}

@app.get("/analyze")
def analyze_sample():
    sample_tracks = [
        {"track_name": "Song A", "artist_name": "Artist 1", "artist_popularity": 90, "genres": ["pop", "dance pop"]},
        {"track_name": "Song B", "artist_name": "Artist 1", "artist_popularity": 90, "genres": ["pop"]},
        {"track_name": "Song C", "artist_name": "Artist 2", "artist_popularity": 40, "genres": ["alt", "indie"]},
        {"track_name": "Song D", "artist_name": "Artist 3", "artist_popularity": 20, "genres": ["hip hop"]},
        {"track_name": "Song E", "artist_name": "Artist 2", "artist_popularity": 40, "genres": ["indie"]},
    ]
    return analyze(sample_tracks)

@app.get("/recommend")
def recommend_sample():
    tracks = [
        {"track_name": "Song A", "artist_name": "Artist 1", "artist_popularity": 90, "genres": ["pop", "dance pop"]},
        {"track_name": "Song B", "artist_name": "Artist 1", "artist_popularity": 90, "genres": ["pop"]},
        {"track_name": "Song C", "artist_name": "Artist 2", "artist_popularity": 40, "genres": ["alt", "indie"]},
        {"track_name": "Song D", "artist_name": "Artist 3", "artist_popularity": 20, "genres": ["hip hop"]},
        {"track_name": "Song E", "artist_name": "Artist 2", "artist_popularity": 40, "genres": ["indie"]},
    ]

    candidates = [
        {"track_name": "Try Me", "artist_name": "Artist 4", "artist_popularity": 15, "genres": ["indie", "alt"]},
        {"track_name": "Louder", "artist_name": "Artist 5", "artist_popularity": 75, "genres": ["pop"]},
        {"track_name": "No Rules", "artist_name": "Artist 6", "artist_popularity": 25, "genres": ["hip hop"]},
        {"track_name": "Blue Hour", "artist_name": "Artist 2", "artist_popularity": 40, "genres": ["indie"]},
        {"track_name": "Sidequest", "artist_name": "Artist 7", "artist_popularity": 10, "genres": ["dance pop"]},
    ]

    return {"recommendations": recommend(tracks, candidates, k=5, allow_familiar=False)}

@app.get("/analyze_spotify")
async def analyze_spotify(limit: int = 50):
    raw = await spotify_get(f"/me/player/recently-played?limit={limit}")

    artist_ids = []
    for item in raw.get("items", []):
        track = item.get("track", {})
        artists = track.get("artists", [])
        if artists:
            artist_ids.append(artists[0]["id"])

    seen = set()
    artist_ids_unique = [a for a in artist_ids if a and not (a in seen or seen.add(a))]

    ids_param = ",".join(artist_ids_unique[:50])
    artists_data = await spotify_get(f"/artists?ids={ids_param}")
    lookup = {a["id"]: a for a in artists_data.get("artists", []) if a}

    tracks = []
    for item in raw.get("items", []):
        t = item.get("track", {})
        artists = t.get("artists", [])
        if not artists:
            continue
        artist = artists[0]
        artist_full = lookup.get(artist["id"], {})
        tracks.append({
            "track_name": t.get("name", "Unknown"),
            "artist_name": artist.get("name", "Unknown"),
            "artist_popularity": artist_full.get("popularity", 0),
            "genres": artist_full.get("genres", []),
        })

    return analyze(tracks)

@app.get("/recommend_spotify")
async def recommend_spotify(history_limit: int = 25, candidate_limit: int = 60, k: int = 10):
   
    raw = await spotify_get(f"/me/player/recently-played?limit={history_limit}")

    artist_ids = []
    for item in raw.get("items", []):
        track = item.get("track", {})
        artists = track.get("artists", [])
        if artists:
            artist_ids.append(artists[0]["id"])

    seen = set()
    artist_ids_unique = [a for a in artist_ids if a and not (a in seen or seen.add(a))]

    ids_param = ",".join(artist_ids_unique[:50])
    artists_data = await spotify_get(f"/artists?ids={ids_param}")
    lookup = {a["id"]: a for a in artists_data.get("artists", []) if a}

    tracks = []
    for item in raw.get("items", []):
        t = item.get("track", {})
        artists = t.get("artists", [])
        if not artists:
            continue
        artist = artists[0]
        artist_full = lookup.get(artist["id"], {})
        tracks.append({
            "track_name": t.get("name", "Unknown"),
            "artist_name": artist.get("name", "Unknown"),
            "artist_popularity": artist_full.get("popularity", 0),
            "genres": artist_full.get("genres", []),
        })

   


    genre_counter = Counter()
    for a in lookup.values():
        for g in a.get("genres", []):
            genre_counter[g] += 1

    top_genres = [g for g, _ in genre_counter.most_common(3)]
    if not top_genres:
        top_genres = ["r&b", "hip-hop", "pop"]

    candidates_raw = []
    for g in top_genres:
        q = urllib.parse.quote(f'genre:"{g}"')
        data = await spotify_get(f"/search?q={q}&type=track&limit=20")
        candidates_raw.extend(data.get("tracks", {}).get("items", []))

   
    cand_artist_ids = []
    for t in candidates_raw:
        artists = t.get("artists", [])
        if artists:
            cand_artist_ids.append(artists[0]["id"])

    seen2 = set()
    cand_artist_ids_unique = [a for a in cand_artist_ids if a and not (a in seen2 or seen2.add(a))]
    ids_param2 = ",".join(cand_artist_ids_unique[:50])
    artists_data2 = await spotify_get(f"/artists?ids={ids_param2}")
    lookup2 = {a["id"]: a for a in artists_data2.get("artists", []) if a}

    candidates = []
    for t in candidates_raw:
        artists = t.get("artists", [])
        if not artists:
            continue
        artist = artists[0]
        artist_full = lookup2.get(artist["id"], {})
        candidates.append({
            "track_name": t.get("name", "Unknown"),
            "artist_name": artist.get("name", "Unknown"),
            "artist_popularity": artist_full.get("popularity", 0),
            "genres": artist_full.get("genres", []),
        })

   

    seen3 = set()
    deduped = []
    for c in candidates:
        key = (c["track_name"].lower(), c["artist_name"].lower())
        if key in seen3:
            continue
        seen3.add(key)
        deduped.append(c)
    candidates = deduped[:candidate_limit]

   

    analysis_result = analyze(tracks)
    rec_result = recommend(tracks, candidates, k=k, allow_familiar=False)

    return {
        "top_genres_used": top_genres,
        "analysis": analysis_result,
        "recommendations": rec_result,
    }
