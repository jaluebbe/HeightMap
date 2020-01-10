import requests
import json

url = 'http://127.0.0.1:8000/api/get_track_length'

payload = [
    {'lat': 47.94, 'lon': 8.3},
    {'lat': 47.56, 'lon': 9.5},
    {'lat': 50.91, 'lon': 6.51},
    {'lat': 52.8, 'lon': 7.4},
    {'lat': 52.78, 'lon': 7.4},
    {'lat': 52.588, 'lon': 7.294},
    {'lat': 53.8, 'lon': 6.9},
    {'lat': 52.740013, 'lon': 5.420472},
    {'lat': 51.5, 'lon': -0.12}]

r = requests.post(url, json=payload)

if r.status_code == 200:
    print(f'{round(r.json() / 1e3, 3)} km')
