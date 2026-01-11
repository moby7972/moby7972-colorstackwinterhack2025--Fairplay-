from __future__ import annotations
import os
import secrets
import urllib.parse
import httpx
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from collections import Counter


router = APIRouter(prefix="/auth", tags=["spotify"])
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE = "https://api.spotify.com/v1"
TOKEN_STORE: dict[str, str] = {}



def get_env(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise RuntimeError(f"Missing env var: {name}")
    return val


@router.get("/login")
def login():
    client_id = get_env("SPOTIFY_CLIENT_ID")
    redirect_uri = get_env("SPOTIFY_REDIRECT_URI")

    state = secrets.token_urlsafe(16)

    scope = "user-read-recently-played user-top-read"

    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,
        "show_dialog": "true",
    }

    url = SPOTIFY_AUTH_URL + "?" + urllib.parse.urlencode(params)
    return RedirectResponse(url)


@router.get("/callback")
async def callback(code: str, state: str | None = None):
    client_id = get_env("SPOTIFY_CLIENT_ID")
    client_secret = get_env("SPOTIFY_CLIENT_SECRET")
    redirect_uri = get_env("SPOTIFY_REDIRECT_URI")

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(SPOTIFY_TOKEN_URL, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        r.raise_for_status()
        token_json = r.json()
        TOKEN_STORE["access_token"] = token_json["access_token"]

    return {"status": "ok", "message": "Spotify connected. Now visit /spotify/me or /spotify/recent."}

async def spotify_get(path: str) -> dict:
    access_token = TOKEN_STORE.get("access_token")
    if not access_token:
        raise RuntimeError("No access token stored. Visit /auth/login first.")

    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        r = await client.get(SPOTIFY_API_BASE + path, headers=headers)
        if r.status_code >= 400:
            raise RuntimeError(f"Spotify error {r.status_code}: {r.text}")
    return r.json()


@router.get("/me")
async def me():
    return await spotify_get("/me")

@router.get("/recent_raw")
async def recent_raw(limit: int = 25):
    return await spotify_get(f"/me/player/recently-played?limit={limit}")


@router.get("/recent_normalized")
async def recent_normalized(limit: int = 25):
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

    return {"count": len(tracks), "tracks": tracks[:10]}

@router.get("/recommendation_candidates")
async def recommendation_candidates(limit: int = 25):
    
    
    raw = await spotify_get("/me/player/recently-played?limit=25")

    

    artist_ids = []
    for item in raw.get("items", []):
        t = item.get("track", {})
        artists = t.get("artists", [])
        if artists:
            artist_ids.append(artists[0]["id"])

    

    seen = set()
    artist_ids_unique = [a for a in artist_ids if a and not (a in seen or seen.add(a))]
    ids_param = ",".join(artist_ids_unique[:50])

   

    artists_data = await spotify_get(f"/artists?ids={ids_param}")
    artists_list = [a for a in artists_data.get("artists", []) if a]

    

    genre_counter = Counter()
    for a in artists_list:
        for g in a.get("genres", []):
            genre_counter[g] += 1

    top_genres = [g for g, _ in genre_counter.most_common(3)]
    if not top_genres:
        # fallback if Spotify returns empty genres for your artists
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
    
    seen = set()
    deduped = []
    for c in candidates:
        key = (c["track_name"].lower(), c["artist_name"].lower())
        if key in seen:
            continue
        seen.add(key)
        deduped.append(c)

    candidates = deduped


    return {
        "top_genres_used": top_genres,
        "count": len(candidates),
        "candidates": candidates[:limit],
    }
