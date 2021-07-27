from os import openpty
import subprocess
import json
import re
from datetime import datetime
import iso8601
import pathlib
import pytz

path = str(pathlib.Path(__file__).parent.resolve())

database = json.loads(open((path +'/database.json'), 'rt').read())

try:
	speed_test = json.loads(subprocess.check_output(['/usr/local/bin/speedtest', '--json']))
except subprocess.CalledProcessError as e:
        speed_test = {'download': 0, 'upload': 0, 'ping': 0}

database.append(speed_test)

f = open((path +'/database.json'), 'w')
f.write(json.dumps(database))
f.close()

template = open((path +'/template.hbs'), 'rt')

labels = []
for data in database:
    if 'timestamp' in data:
        tz = pytz.timezone('Europe/Rome')
        labels.append(iso8601.parse_date(data['timestamp']).astimezone(tz).strftime("%d/%m/%Y %H:%M"))

downloads = []
for data in database:
    if 'download' in data:
        downloads.append( int(data['download']) / 1000000 )

uploads = []
for data in database:
    if 'upload' in data:
        uploads.append( int(data['upload']) / 1000000 )

pings = []
for data in database:
    if data['ping']:
        pings.append(data['ping'])

html = template.read()
html = re.sub('{{ labels }}', json.dumps(labels), html)
html = re.sub('{{ downloads }}', json.dumps(downloads), html)
html = re.sub('{{ uploads }}', json.dumps(uploads), html)
html = re.sub('{{ pings }}', json.dumps(pings), html)
template.close()

output = open((path +'/public/history.html'), 'w')
output.write(html)
output.close()
