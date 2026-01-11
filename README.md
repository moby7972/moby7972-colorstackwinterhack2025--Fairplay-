# 🎧 FairPlay — Responsible Music Recommendations

FairPlay is a **Responsible AI music recommendation system** that helps users understand and correct popularity bias in algorithmic music discovery.

Instead of treating recommendation algorithms as black boxes, FairPlay:
- Audits a user’s listening behavior
- Quantifies how much discovery they’re actually getting
- Generates transparent, fairness-aware recommendations that preserve taste while elevating emerging artists

Every recommendation comes with a **clear explanation**, and users can directly control how strongly fairness is applied.

---

## 🌍 Inspiration

Music recommendation systems shape what artists get heard—but often invisibly.  
While using Spotify, I noticed that even with diverse tastes across genres like dancehall, afrobeats, and soca, recommendations still leaned heavily toward familiar or already popular artists.

This raised a simple but powerful question:

> **How much discovery am I actually getting—and who is being left out by default?**

FairPlay was built to make recommendation systems more **transparent, accountable, and human-centered**, especially in creative spaces where exposure matters.

---

## 🎯 What FairPlay Does

### 1️⃣ Listening Bias Audit
FairPlay analyzes recent Spotify listening history and computes:
- Total tracks and unique artists
- Genre diversity
- Popularity distribution:
  - Mainstream
  - Mid-popularity
  - Emerging
- An **Exploration Score** that quantifies discovery behavior

### 2️⃣ Fairness-Aware Recommendations
Instead of optimizing purely for popularity:
- Candidate tracks are generated from the user’s **actual genre preferences**
- Artists are re-ranked to counter popularity bias
- Emerging and mid-popularity artists are intentionally elevated

### 3️⃣ Full Transparency
Each recommendation includes a clear explanation such as:
- New vs familiar artist
- Genre match
- Artist popularity tier

No hidden logic. No black box.

### 4️⃣ User Control
Users can tune how strongly fairness is applied via a `fairness_strength` parameter—making the algorithm **accountable and adjustable**.

---

## 🧠 How It Works

1. **Spotify Authentication**
   - Users authenticate via Spotify OAuth
   - Recent listening history is fetched securely

2. **Audit Phase**
   - Builds a listening profile from recent tracks
   - Computes popularity bias and exploration metrics

3. **Candidate Generation**
   - Extracts top genres from recent listening
   - Searches Spotify for tracks in those genres
   - Avoids popularity-only ranking

4. **Fair Ranking**
   - Scores tracks using:
     - Genre relevance
     - Artist novelty
     - Popularity fairness adjustment

Mathematically, fairness is introduced as:

$$
\text{score} = \text{relevance} + \alpha \cdot \left(\frac{100 - \text{artist popularity}}{50}\right)
$$

Where \\(\alpha\\) is a user-controlled fairness parameter.

---

## 📊 Example Output

```json
{
  "top_genres_used": ["dancehall", "afrobeats", "soca"],
  "analysis": {
    "bias_summary": "Your listening is fairly balanced but leans toward familiar artists (76.0%).",
    "exploration_score": 40.4
  },
  "recommendations": {
    "new_artist_rate": 100.0,
    "avg_recommended_popularity": 28.2,
    "items": [
      {
        "track_name": "The System",
        "artist_name": "Courtney Melody",
        "score": 7.54,
        "reason": "new artist; genre match: dancehall, reggae; emerging (23%)"
      }
    ]
  }
}
```
---

## ⚖️ Responsible AI Alignment

FairPlay is intentionally designed around Responsible AI principles:

### ✅ Transparency
Every recommendation includes human-readable reasoning
Candidate generation logic is explicit and explainable

### ✅ Fairness
Actively counteracts popularity bias
Promotes discovery of emerging and underrepresented artists

### ✅ Accountability
User-adjustable fairness strength
No opaque ranking logic

### ✅ Human-Centered Design
Preserves user taste through genre matching
Balances relevance with ethical discovery

---

## 🛠 Tech Stack

Language: Python 3.12

Framework: FastAPI

APIs: Spotify Web API

Authentication: OAuth 2.0

HTTP Client: httpx

Environment Management: python-dotenv

---

## 📦 Installation & Setup
Run in your terminal:
### 1️⃣ Clone the Repository
```
git clone https://github.com/moby7972/moby7972-colorstackwinterhack2025--Fairplay-.git
```
### 2️⃣ Create and Activate Virtual Environment
```
python -m venv .venv
```
```
.\.venv\Scripts\Activate.ps1
```
### 3️⃣ Install Dependencies
```
pip install fastapi uvicorn httpx python-dotenv
```
### 4️⃣ Create .env File
Create a `.env` file in the project root with the following values:

SPOTIFY_CLIENT_ID — from Spotify Developer Dashboard  
SPOTIFY_CLIENT_SECRET — from Spotify Developer Dashboard  
SPOTIFY_REDIRECT_URI — must match the redirect URI configured in your Spotify app

Example:

```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/auth/callback
```
### 5️⃣ Run the Server
```
uvicorn app.main:app --reload
```
### 6️⃣ Authenticate with Spotify
Open in your browser:
```
http://127.0.0.1:8000/auth/login
```

## 🔗 API Endpoints
| Endpoint                                   | Description                    |
| ------------------------------------------ | ------------------------------ |
| `/auth/login`                              | Spotify OAuth login            |
| `/analyze_spotify`                         | Audit listening behavior       |
| `/auth/recommendation_candidates`          | Generate fair candidate tracks |
| `/recommend_spotify`                       | Full audit + recommendations   |
| `/recommend_spotify?fairness_strength=2.0` | Stronger fairness bias         |

## 🎥 Demo

Video Demo: (Add link here)

GitHub Repo: https://github.com/moby7972/moby7972-colorstackwinterhack2025--Fairplay-.git

## 👤 Author

Built by Moby | 
ColorStack Winter Hackathon 2025



