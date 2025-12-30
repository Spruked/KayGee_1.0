import requests, sys, json

try:
    r = requests.post('http://localhost:8000/visualization/space_field', json={'sides':5,'levels':3,'width':400,'height':200}, timeout=20)
    print('STATUS', r.status_code)
    print('\n---TEXT (first 4000 chars)---\n')
    print(r.text[:4000])
    print('\n---TRY JSON---\n')
    try:
        j = r.json()
        print('json keys:', list(j.keys()))
    except Exception as e:
        print('response not JSON:', e)
except Exception as e:
    print('ERR', e)
    sys.exit(2)
