import requests

KNOWN_JOKES = ["Why couldn't the produce manager make it to work? He could drive, but he didn't avocado.", 
               "How is my wallet like an onion? Every time I open it, I cry.", 
               'Hi, I’m Cliff. Drop over sometime.'
               ]

JOKES_TWO_URL = "https://v2.jokeapi.dev/joke/Programming,Pun?blacklistFlags=nsfw,religious,political,racist,sexist,explicit&type=twopart"
JOKES_URL = "https://v2.jokeapi.dev/joke/Programming,Pun?blacklistFlags=nsfw,religious,political,racist,sexist,explicit&type=single"

def get_joke(joke_type: str | None = None) -> dict | None:
    url = "https://v2.jokeapi.dev/joke/Programming,Pun"
    params = {
        "lang": "en",
        "blacklistFlags": "nsfw,religious,political,racist,sexist,explicit",
    }
    if joke_type:
        params["type"] = joke_type
    response = requests.get(url, params)
    if response.status_code != 200:
        return None # None можно не писать
    json_data: dict = response.json()
    if json_data.get("error"):
        return None
    
    return json_data

def get_random_joke():
    json_data = get_joke("single")
    if not json_data:
        return "Error"

    return json_data["joke"]

def get_random_joke_two():
    json_data = get_joke("twopart")
    if not json_data:
        return "Error"

    return json_data["setup"], json_data["delivery"]