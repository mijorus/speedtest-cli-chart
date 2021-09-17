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
    speed_test = json.loads(subprocess.check_output(['/usr/local/bin/speedtest', '--json']))
except subprocess.CalledProcessError as e:
    speed_test = {'download': 0, 'upload': 0, 'ping': 0}

database.append(speed_test)
db_create(database)

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
    
    if 'download' in data:
        downloads.append( int(data['download']) / 1000000 )

    if 'upload' in data:
        uploads.append( int(data['upload']) / 1000000 )

    if data['ping']:
        pings.append(data['ping'])

    if 'server' in data:
        server = servers[data['server']['id']] if data['server']['id'] in servers else {}
        servers[data['server']['id']] = {
            'name': data['server']['name'] + ' ' + (data['server']['sponsor'] if 'sponsor' in data['server'] else ''), 
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
