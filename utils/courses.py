import requests

def get_courses(api_key, skill="python"):
    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": f"{skill} course",   # 🔥 dynamic search
        "key": api_key,
        "maxResults": 12,         # 🔥 more results
        "type": "video"
    }

    response = requests.get(url, params=params)
    data = response.json()

    courses = []

    for item in data.get("items", []):
        if "videoId" in item.get("id", {}):
            video_id = item["id"]["videoId"]

            courses.append({
                "title": item["snippet"]["title"],
                "link": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"]
            })

    return courses