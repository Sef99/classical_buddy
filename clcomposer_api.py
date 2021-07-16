import requests
import random
from decouple import config

def get_composerdet(name):
    url = "https://api.openopus.org/composer/list/search/"+ name + ".json"
    r = requests.get(url)
    r_data = r.json()
    return r_data

def get_random():
    ran_num = random.randrange(0, 220, 1)
    url = "https://api.openopus.org/composer/list/ids/"+ str(ran_num) + ".json"
    r = requests.get(url)
    r_data = r.json()
    return r_data
    
def get_workdet(comp_id):
    url = 'https://api.openopus.org/work/list/composer/'+ str(comp_id) + '/genre/Popular.json'
    r = requests.get(url)
    r_data = r.json()
    return r_data

def wikiapi(name):
    url = 'https://en.wikipedia.org/w/api.php?format=json&action=query&indexpageids=true&prop=extracts&exintro&explaintext&redirects=1&titles=' + str(name)
    r = requests.get(url)
    r_data = r.json()
    return r_data

def yt_api(name):
    url = 'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q=' + name + '&type=video&key=' + config('YT_API_KEY')
    r = requests.get(url)
    r_data = r.json()
    return r_data