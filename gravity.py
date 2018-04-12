import re
import requests
import dnslib
import dbm
import os

gravity = dbm.open('gravity.dbm', 'nf')
whitelist = dict()

source = 'https://raw.githubusercontent.com/barnsza/bcfr/master/sources.txt'
seen_urls = set()

def process_record(record):
    if record[0] == '!':
        whitelist['{0}.'.format(record[1:])] = b''
    else:
        gravity['{0}.'.format(record)] = b''

def process_url(url):
    if url in seen_urls:
        return
    seen_urls.add(url)
    print(url)

    try:
        data = requests.get(url).text.split('\n')
    except:
        print('Error fetching source')
        return

    for record in data:
        record = re.split('#|(?<!:)//', record)[0].split()
        if len(record) == 0:
            continue
        elif len(record) == 1:
            if re.search('https?://', record[0]):
                process_url(record[0])
            else:
                process_record(record[0])
        else:
            process_record(record[1])

process_url(source)

for d in whitelist:
    try:
        del gravity[d]
    except:
        pass

count = len(gravity)
gravity.reorganize()
gravity.sync()
gravity.close()
size = os.path.getsize('gravity.dbm')

print('Stats: {0} domains, {1} bytes.'.format(count, size))
