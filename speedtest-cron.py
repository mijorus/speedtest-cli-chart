from os import openpty
import subprocess
import json
import re
from datetime import datetime
import iso8601

database = json.loads(open('./database.json', 'rt').read())
speed_test = json.loads(subprocess.check_output(['speedtest', '--json']))

database.append(speed_test)

f = open('./database.json', 'w')
f.write(json.dumps(database))
f.close()

template = open('./template.hbs', 'rt')

labels = []
for data in database:
    if data['timestamp']:
        labels.append(iso8601.parse_date(data['timestamp']).strftime("%d/%m/%Y"))

labels = []
for data in database:
    if data['timestamp']:
        labels.append(iso8601.parse_date(data['timestamp']).strftime("%d/%m/%Y"))

downloads = []
for data in database:
    if data['download']:
        downloads.append( int(data['download']) / 1000000 )

uploads = []
for data in database:
    if data['upload']:
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

output = open('./history.html', 'w')
output.write(html)