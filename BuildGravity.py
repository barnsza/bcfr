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

seen_urls = set()

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
                gravity['{0}.'.format(record[0])] = None
        else:
            gravity['{0}.'.format(record[1])] = None

for source in sources:
    process_url(source)

print('Stats: {0} domains, {1} bytes.'.format(gravity.count(), gravity.size()))

gravity.close()
