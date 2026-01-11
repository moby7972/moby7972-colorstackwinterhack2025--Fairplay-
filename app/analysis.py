from __future__ import annotations
from collections import Counter
from typing import Any

def analyze(tracks: list[dict[str, Any]]) -> dict[str, Any]:
    if len(tracks) == 0:
        return {
            "total_tracks": 0,
            "unique_artists": 0,
            "avg_artist_popularity": 0.0,
            "unique_genres": 0,
            "top_artists": [],
            "popularity_distribution": {},
            "bias_summary": '',
            "exploration_score": 0
        }

    unique_artists = set()
    unique_genres = set()
    artist_counter = Counter()
    popularity_sum = 0
    mainstream_count = 0
    mid_count = 0
    emerging_count = 0

    for track in tracks:
        unique_artists.add(track['artist_name'])
        artist_counter[track["artist_name"]] += 1
        popularity_sum += track['artist_popularity']
        for genre in track['genres']:
            unique_genres.add(genre)
        if track['artist_popularity'] >= 70:
            mainstream_count += 1
        elif track['artist_popularity'] >= 30:
            mid_count += 1
        else:
            emerging_count += 1

    avg_popularity = popularity_sum / len(tracks)

    top_artists = [
        {"artist_name": name, "count": count}
        for name, count in artist_counter.most_common(5)
    ]

    mainstream_pct = round((mainstream_count / len(tracks)) * 100, 2) if len(tracks) else 0
    mid_pct = round((mid_count / len(tracks)) * 100, 2) if len(tracks) else 0
    emerging_pct = round((emerging_count / len(tracks)) * 100, 2) if len(tracks) else 0

    popularity_distribution = {
        "mainstream": mainstream_pct,
        "mid": mid_pct,
        "emerging": emerging_pct,
    }

    dominant = max(popularity_distribution, key=popularity_distribution.get)
    dominant_pct = popularity_distribution[dominant]

    if dominant == "mainstream":
        bias_summary = (
            f"Your listening heavily favors mainstream artists ({dominant_pct}%), "
            "which may limit discovery of emerging artists."
        )
    elif dominant == "mid":
        bias_summary = (
            f"Your listening is fairly balanced but leans toward familiar artists ({dominant_pct}%)."
        )
    else:
        bias_summary = (
            f"Your listening strongly supports emerging artists ({dominant_pct}%) and musical exploration."
        )

    exploration_score = emerging_pct * 1.0 + mid_pct * 0.5 + mainstream_pct * 0.1

    return {
        "total_tracks": len(tracks),
        "unique_artists": len(unique_artists),
        "avg_artist_popularity": round(avg_popularity, 2),
        "unique_genres": len(unique_genres),
        "top_artists": top_artists,
        "popularity_distribution": popularity_distribution,
        "bias_summary": bias_summary,
        "exploration_score": round(exploration_score, 2)
    }

def recommend(
    tracks: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    k: int = 5,
    allow_familiar: bool = False
) -> list[dict[str, Any]]:

    listened_artists = set()
    liked_genres = Counter()

    for track in tracks:
        listened_artists.add(track['artist_name'])
        for g in track["genres"]:
            liked_genres[g] += 1


    top_k = []

    for candidate in candidates:
        score = 0
        reasons = []
        if candidate['artist_name'] not in listened_artists:
            score += 3
            reasons.append("new artist")
        else:
            if allow_familiar is False:
                continue
            else:
                reasons.append("familiar artist")
        genre_match = []
        for genre in candidate['genres']:
            if genre in liked_genres:
                genre_match.append(genre)
        if genre_match:
            score += min(3, max(2, len(genre_match)))
            reasons.append("genre match: " + ", ".join(genre_match))
        score += (100 - candidate['artist_popularity']) / 50
        if candidate['artist_popularity'] < 30:
            reasons.append(f"emerging ({candidate['artist_popularity']}%)")
        elif candidate['artist_popularity'] < 70:
            reasons.append(f"mid ({candidate['artist_popularity']}%)")
        else:
            reasons.append(f"mainstream ({candidate['artist_popularity']}%)")
        top_k.append({
            "track_name": candidate['track_name'],
            "artist_name": candidate['artist_name'],
            "artist_popularity": candidate['artist_popularity'],
            "score": round(score, 2),
            "reason": "; ".join(reasons)
        })

    ranked = sorted(top_k, key=lambda x: (-x["score"], x["artist_popularity"], x["track_name"]))[:k]

    popularity_sum = 0
    new_artist_count = sum(1 for item in ranked if item["artist_name"] not in listened_artists)


    for artist in ranked:
        popularity_sum += artist['artist_popularity']

    return {
        "recommended_count": len(ranked),
        "new_artist_rate": round((new_artist_count / len(ranked)) * 100, 2) if ranked else 0,
        "avg_recommended_popularity": round(popularity_sum / len(ranked), 2) if len(ranked) else 0,
        "items": ranked
    }



