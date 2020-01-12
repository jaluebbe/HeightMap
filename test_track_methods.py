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
    print(f'{r.json()}')
else:
    print(r.status_code)

print('# test_track:')
payload = test_track
r = requests.post(url, json=payload)
if r.status_code == 200:
    print(f'{r.json()}')
else:
    print(r.status_code)

print('### Testing /api/get_simplified_track ###')
url = 'http://127.0.0.1:8000/api/get_simplified_track'

straight_track_segments = [
    {'lat': 51, 'lon': 8},
    {'lat': 51.3, 'lon': 8},
    {'lat': 51.5, 'lon': 8},
    {'lat': 51.6, 'lon': 8},
    {'lat': 52, 'lon': 8},
    {'lat': 53, 'lon': 8},
    {'lat': 52, 'lon': 7},
    {'lat': 51, 'lon': 6}
    ]

latitude_disturbed_track = [
    {'lat': 45, 'lon': -2},
    {'lat': 44.9999991, 'lon': -1},  # 0.1m off the straight line
    {'lat': 45, 'lon': 0},
    {'lat': 45.000009, 'lon': 1},  # 1m off the straight line
    {'lat': 45, 'lon': 2},
    {'lat': 44.99991, 'lon': 3},  # 10m off the straight line
    {'lat': 45, 'lon': 4},
    {'lat': 45.009, 'lon': 5},  # 100m off the straight line
    {'lat': 45, 'lon': 6},
    {'lat': 44.991, 'lon': 7},  # 1000m off the straight line
    {'lat': 45, 'lon': 8},
    {'lat': 45.09, 'lon': 9},  # 10002m off the straight line
    {'lat': 45, 'lon': 10}
    ]

longitude_disturbed_track = [
    {'lat': 39, 'lon': 0},
    {'lat': 40, 'lon': 0.0000012},  # 0.1m off the straight line
    {'lat': 41, 'lon': 0},
    {'lat': 42, 'lon': -0.000012},  # 1m off the stright line
    {'lat': 43, 'lon': 0},
    {'lat': 44, 'lon': 0.00013},  # 10m off the stright line
    {'lat': 45, 'lon': 0},
    {'lat': 46, 'lon': -0.00129},  # 100m off the straight line
    {'lat': 47, 'lon': 0},
    {'lat': 48, 'lon': 0.0134},  # 1000m off the straight line
    {'lat': 49, 'lon': 0},
    {'lat': 50, 'lon': -0.14},  # 10037m off the straight line
    {'lat': 51, 'lon': 0},
    ]

print('# straight_track_segments:')
payload = {'track': straight_track_segments}
r = requests.post(url, json=payload)
if r.status_code == 200:
    print(f'{r.json()}')
else:
    print(r.status_code)

print('# latitude_disturbed_track:')
for epsilon in [0.1, 0.01, 0.001, 1e-4, 1e-5, 1e-6, 1e-7, 0]:
    payload = {'track': latitude_disturbed_track, 'epsilon': epsilon}
    r = requests.post(url, json=payload)
    if r.status_code == 200:
        print(f'epsilon={epsilon}, remaining points={len(r.json())}')
    else:
        print(r.status_code)

print('# longitude_disturbed_track:')
for epsilon in [0.1, 0.01, 0.001, 1e-4, 1e-5, 1e-6, 1e-7, 0]:
    payload = {'track': longitude_disturbed_track, 'epsilon': epsilon}
    r = requests.post(url, json=payload)
    if r.status_code == 200:
        print(f'epsilon={epsilon}, remaining points={len(r.json())}')
    else:
        print(r.status_code)
