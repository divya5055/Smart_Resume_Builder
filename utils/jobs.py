# utils/jobs.py

import requests

def get_jobs(query="software developer", location="India"):

    url = "https://jsearch.p.rapidapi.com/search"

    headers = {
        "X-RapidAPI-Key": "2ec069a7e1msh891a614d8c9be30p155819jsn22661e4e8780",
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    params = {
        "query": f"{query} in {location}",   # ✅ ADD THIS
        "page": "1",
        "num_pages": "1"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        return data.get("data", [])
    
    except Exception as e:
        print("Error fetching jobs:", e)
        return []