import requests
import json

simple_test_track = [
    {'lat': 52.1346, 'lon': 7.6848},
    {'lat': 51.5, 'lon': -0.12}]
test_track = [
    {'lat': 47.94, 'lon': 8.3},
    {'lat': 47.56, 'lon': 9.5},
    {'lat': 50.91, 'lon': 6.51},
    {'lat': 52.1346, 'lon': 7.6848},
    {'lat': 52.8, 'lon': 7.4},
    {'lat': 52.78, 'lon': 7.4},
    {'lat': 52.588, 'lon': 7.294},
    {'lat': 53.8, 'lon': 6.9},
    {'lat': 52.740013, 'lon': 5.420472},
    {'lat': 51.5, 'lon': -0.12}]

print('### Testing /api/get_track_length ###')
url = 'http://127.0.0.1:8000/api/get_track_length'

print('# simple_test_track:')
payload = simple_test_track
r = requests.post(url, json=payload)
if r.status_code == 200:
    print(f'{r.json()} m')
else:
    print(r.status_code)

print('# test_track:')
payload = test_track
r = requests.post(url, json=payload)
if r.status_code == 200:
    print(f'{r.json()} m')
else:
    print(r.status_code)

print('### Testing /api/get_track_position ###')
url = 'http://127.0.0.1:8000/api/get_track_position'

print('# simple_test_track:')
for distance in [0, 250e3, 542538.395, 542538.396, 600e3]:
    payload = {'track': simple_test_track, 'distance': distance}
    r = requests.post(url, json=payload)
    if r.status_code == 200:
        print(r.json())
    else:
        print(r.status_code)

print('# test_track:')
for distance in [0, 250e3, 500e3, 1e4, 1485833.003, 1485833.004, 1500e3]:
    payload = {'track': test_track, 'distance': distance}
    r = requests.post(url, json=payload)
    if r.status_code == 200:
        print(r.json())
    else:
        print(r.status_code)

print('### Testing /api/get_track_elevation ###')
url = 'http://127.0.0.1:8000/api/get_track_elevation'

print('# simple_test_track:')
payload = simple_test_track
r = requests.post(url, json=payload)
if r.status_code == 200:
    print(f'{r.json()} m')
else:
    print(r.status_code)

print('# test_track:')
payload = test_track
r = requests.post(url, json=payload)
if r.status_code == 200:
    print(f'{r.json()} m')
else:
    print(r.status_code)
