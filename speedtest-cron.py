import subprocess
import json
import re
import iso8601
import pathlib
import pytz
import time
import random
import os
import sys

if not '--no-sleep' in sys.argv:
    time.sleep(random.randint(10, 40))

path = str(pathlib.Path(__file__).parent.resolve())

def db_create(content, filename = 'database.json'):
    f = open((path +'/database/'+filename), 'w')
    f.write(json.dumps(content))
    f.close()

try:
    database = json.loads(open((path +'/database/database.json'), 'rt').read())
except:
    database = []

db_create(database, 'database_backup.json')

try:
    # speed_test_path = subprocess.check_output(['which', 'speedtest']).decode('UTF-8').replace('\n', '')
    speed_test = json.loads(subprocess.check_output(['/home/pi/.local/bin/speedtest', '--format=json']))
except subprocess.CalledProcessError as Exeption:
    print(Exception)
    speed_test = {
        'download': {
            'bytes': 0,
        }, 
        'upload': {
            'bytes': 0,
        }, 
        'ping': {
            'latency': 0
        }
    }

database.append(speed_test)
db_create(database)

if '--show' in sys.argv:
    print('Download: '+str(int(speed_test['download']['bytes']) * 8 / 10000000 )+' Mbit/s\nUpload: '+str(int(speed_test['upload']['bytes']) * 8 / 10000000 ) + ' Mbit/s\nPing: '+str(speed_test['ping']['latency'])+'s')


template = open((path +'/template.hbs'), 'rt')

labels = []
downloads = []
uploads = []
pings = []
servers = {}
for data in database:
    if 'timestamp' in data:
        tz = pytz.timezone('Europe/Rome')
        labels.append(iso8601.parse_date(data['timestamp']).astimezone(tz).strftime("%d/%m/%Y %H:%M"))
    
    if 'download' in data and (type(data['download']) is float or type(data['download']) is int):
        downloads.append( int(data['download']) / 1000000 )
    else:
        downloads.append( data['download']['bytes'] * 8 / 10000000 )

    if 'upload' in data and (type(data['upload']) is float or type(data['upload']) is int):
        uploads.append( int(data['upload']) / 1000000 )
    else:
        uploads.append( data['upload']['bytes'] * 8 / 10000000 )

    if 'ping' in data and (type(data['ping']) is float or type(data['ping']) is int):
        pings.append(data['ping'])
    else:
        pings.append(data['ping']['latency'])

    if 'server' in data:
        server = servers[data['server']['id']] if data['server']['id'] in servers else {}
        servers[data['server']['id']] = {
            'name': data['server']['name'], 
            'count': 1 if not 'count' in server else server['count'] + 1
        }

html = template.read()
html = re.sub('{{ labels }}', json.dumps(labels), html)
html = re.sub('{{ downloads }}', json.dumps(downloads), html)
html = re.sub('{{ uploads }}', json.dumps(uploads), html)
html = re.sub('{{ pings }}', json.dumps(pings), html)

s_table = ''
for server_id, s in servers.items():
    s_table = f'{s_table} <tr><td>{server_id}</td><td>{s["name"]}</td><td>{s["count"]}</td></tr>'

html = re.sub('{{ servers_table }}', s_table, html)

template.close()

output = open((path +'/public/history.html'), 'w')
output.write(html)
output.close()
