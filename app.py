from flask import Flask, render_template, request, jsonify
import requests
import os
import random
from dotenv import load_dotenv

load_dotenv()
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

app = Flask(__name__)

# ----------------------------
# Robust emotion/sentiment detection
# ----------------------------
def detect_emotion(text):
    text = text.lower()

    # Joy / Positive
    joy_words = [
        'happy','joy','excited','energetic','thrilled','cheerful','delighted','elated','optimistic',
        'funny','ecstatic','joyful','lively','playful','amused','content'
    ]
    if any(w in text for w in joy_words):
        return 'joy', 'positive'

    # Sadness / Negative
    sadness_words = [
        'sad','lonely','down','heartbroken','depressed','blue','melancholy','gloomy',
        'disappointed','miserable','unhappy','tearful','hopeless'
    ]
    if any(w in text for w in sadness_words):
        return 'sadness', 'negative'

    # Romantic / Positive
    romantic_words = [
        'love','romantic','affectionate','passionate','heartfelt','sweet','adoring',
        'caring','intimate','devoted','tender'
    ]
    if any(w in text for w in romantic_words):
        return 'romantic', 'positive'

    # Angry / Negative
    angry_words = [
        'angry','frustrated','annoyed','upset','irritated','mad','resentful','furious','agitated'
    ]
    if any(w in text for w in angry_words):
        return 'angry', 'negative'

    # Relaxed / Calm / Positive
    relaxed_words = [
        'relaxed','calm','peaceful','chill','serene','tranquil','content','soothing','meditative','restful'
    ]
    if any(w in text for w in relaxed_words):
        return 'relaxed', 'positive'

    # Motivated / Energetic / Positive
    motivated_words = [
        'motivated','determined','confident','strong','powerful','focused','inspired','driven','ambitious'
    ]
    if any(w in text for w in motivated_words):
        return 'motivated', 'positive'

    # Fear / Nervous / Negative
    fear_words = [
        'anxious','nervous','scared','fearful','worried','stressed','tense','afraid','panic','uneasy'
    ]
    if any(w in text for w in fear_words):
        return 'fear', 'negative'

    # Surprise / Curious / Positive
    surprise_words = [
        'surprised','curious','amazed','astonished','intrigued','shocked','wonder'
    ]
    if any(w in text for w in surprise_words):
        return 'surprised', 'positive'

    # Default Neutral
    return 'neutral', 'neutral'


# ----------------------------
# YouTube search with randomization
# ----------------------------
def search_youtube(query, max_results=10):
    # fetch more results to allow random selection
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 20,  # fetch more to randomize
        "videoCategoryId": "10",  # music category
    }
    resp = requests.get(url, params=params).json()
    items = resp.get("items", [])

    if not items:
        return []

    # pick random max_results videos
    selected = random.sample(items, min(max_results, len(items)))

    results = []
    for item in selected:
        video_id = item['id']['videoId']
        results.append({
            "title": item['snippet']['title'],
            "channel": item['snippet']['channelTitle'],
            "video_id": video_id,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "thumbnail": item['snippet']['thumbnails']['high']['url']
        })
    return results


# ----------------------------
# Routes
# ----------------------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/recommend', methods=['POST'])
def recommend():
    text = request.form.get('mood_text', '')
    if not text:
        return jsonify({"error": "No text provided"}), 400

    emotion, sentiment = detect_emotion(text)

    # Build mood-based search queries
    mood_queries = {
        "joy": ["happy songs", "upbeat songs", "feel good music", "party songs", "dance hits"],
        "sadness": ["sad songs", "melancholy music", "emotional music", "slow music", "heartbreak playlist"],
        "romantic": ["romantic songs", "love songs", "soft love music", "sweet melodies", "romance playlist"],
        "angry": ["angry music", "rock hits", "metal songs", "intense music", "rebellious tracks"],
        "relaxed": ["chill music", "calm songs", "relaxing melodies", "ambient music", "peaceful tunes"],
        "motivated": ["motivational songs", "energetic tracks", "power songs", "workout playlist", "inspirational music"],
        "fear": ["suspense music", "tense tracks", "thriller soundtrack", "dramatic instrumentals"],
        "surprised": ["surprising music", "fun upbeat tracks", "unexpected hits", "quirky music"],
        "neutral": ["top hits", "popular music", "trending songs", "latest releases"]
    }

    queries = mood_queries.get(emotion, ["popular songs"])
    query = random.choice(queries)  # pick one randomly

    results = search_youtube(query, max_results=15)  # 15 random songs

    return jsonify({
        "text": text,
        "emotion": emotion,
        "sentiment": sentiment,
        "results": results
    })


if __name__ == "__main__":
    app.run(debug=True)
