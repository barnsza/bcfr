import re
import requests
import dnslib
import kyotocabinet

gravity = kyotocabinet.DB()
gravity.open('gravity.kch', kyotocabinet.DB.OWRITER |
    kyotocabinet.DB.OCREATE | kyotocabinet.DB.OTRUNCATE)

sources = [
    'https://raw.githubusercontent.com/pi-hole/pi-hole/master/adlists.default',
    'https://v.firebog.net/hosts/lists.php?type=tick'
    ]

for source in sources:
    for url in requests.get(source).text.split('\n'):
        url = url.split('#')[0].split()
        if len(url) == 1:
            print(url[0])

            for record in requests.get(url[0]).text.split('\n'):
                record = re.split('[#/]', record)[0].split()
                if len(record) == 0:
                    continue
                elif len(record) == 1:
                    gravity['{0}.'.format(record[0])] = None
                else:
                    gravity['{0}.'.format(record[1])] = None
        else:
            continue

gravity.close()
