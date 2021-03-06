import subprocess
import json
import re
import iso8601
import pathlib
import time
import random
import os
import sys
import datetime

path = str(pathlib.Path(__file__).parent.resolve())

def db_create(content, filename = 'database.json'):
    f = open((path +'/database/'+filename), 'w+')
    f.write(json.dumps(content))
    f.close()

def convert_to_mbps(bytes: int):
    return str(bytes * 8 / 1000000)

def main():
    if not '--no-sleep' in sys.argv:
        time.sleep(random.randint(10, 40))

    try:
        database = json.loads(open((path +'/database/database.json'), 'rt').read())
    except:
        database = []

    db_create(database, 'database_backup.json')

    try:
        source = '/home/pi/.local/bin/speedtest'
        for argv in sys.argv:
            if argv.__contains__('--script-path='):
                source = argv.replace('--script-path=', '')

        speed_test = json.loads(subprocess.check_output([source, '--format=json']))
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
        print('Download: '+convert_to_mbps(speed_test['download']['bandwidth'])+' Mbit/s\nUpload: '+convert_to_mbps(speed_test['upload']['bandwidth'])+ ' Mbit/s\nPing: '+str(speed_test['ping']['latency'])+'s')

    template = open((path +'/template.hbs'), 'rt')

    labels = []
    downloads = []
    uploads = []
    pings = []
    servers = {}

    for data in database:
        if 'timestamp' in data:
            labels.append(iso8601.parse_date(data['timestamp']).strftime("%d/%m/%Y %H:%M"))
        else:
            labels.append('unknown')

        if 'download' in data:
            if type(data['download']) is dict:
                try:
                    downloads.append( convert_to_mbps(data['download']['bandwidth']) )
                except:
                    downloads.append(0)
        
        if 'upload' in data:
            if type(data['upload']) is dict:
                try:
                    uploads.append( convert_to_mbps(data['upload']['bandwidth']) )
                except:
                    uploads.append(0)
        
        if 'ping' in data:
            if type(data['ping']) is dict:
                try:
                    pings.append(data['ping']['latency'])
                except:
                    pings.append(0)

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

    output = open((path +'/public/history.html'), 'w+')
    output.write(html)
    output.close()

if __name__ == '__main__':
    main()