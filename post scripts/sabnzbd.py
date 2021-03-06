#!/usr/bin/env python

# ======================================== #
# ============= INSTRUCTIONS ============= #

# Disable 'Post-Process Only Verified Jobs' in Sabnzbd.
# Add api information to conf:

conf = {
    'watcherapi': 'WATCHERAPIKEY',
    'watcheraddress': 'http://localhost:9090/',
    'sabkey': 'SABAPIKEY',
    'sabhost': 'localhost',
    'sabport': '8080'
}

#  DO NOT TOUCH ANYTHING BELOW THIS LINE!  #
# ======================================== #

import json
import sys

if sys.version_info.major < 3:
    import urllib
    import urllib2
    urlencode = urllib.urlencode
    request = urllib2.Request
    urlopen = urllib2.urlopen
else:
    import urllib.parse
    import urllib.request
    request = urllib.request.Request
    urlencode = urllib.parse.urlencode
    urlopen = urllib.request.urlopen

# Gather info
try:
    status = int(sys.argv[7])
    guid = sys.argv[3].replace('-', ':').replace('+', '/')
except Exception:
    print('Post-processing failed. Incorrect args.')
    sys.exit(1)

watcheraddress = conf['watcheraddress']
watcherapi = conf['watcherapi']
sabkey = conf['sabkey']
sabhost = conf['sabhost']
sabport = conf['sabport']
data = {'apikey': watcherapi, 'guid': ''}

# get guid and nzo_id from sab history, since sab < 2.0 doesn't send with args:
name = urllib2.quote(sys.argv[3], safe='')
url = u'http://{}:{}/sabnzbd/api?apikey={}&mode=history&output=json&search={}'.format(sabhost, sabport, sabkey, name)

request = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
response = urllib2.urlopen(request, timeout=60).read()

slots = json.loads(response)['history']['slots']

for dl in slots:
    if dl['loaded'] is True:
        data['guid'] = dl['url']
        data['downloadid'] = dl['nzo_id']
        break

data['path'] = sys.argv[1]

if status == 0:
    print(u'Sending {} to Watcher as Complete.'.format(name))
    data['mode'] = 'complete'
else:
    print(u'Sending {} to Watcher as Failed.'.format(name))
    data['mode'] = 'failed'

# Send info
url = u'{}/postprocessing/'.format(watcheraddress)
post_data = urlencode(data).encode('ascii')

request = request(url, post_data, headers={'User-Agent': 'Mozilla/5.0'})
response = json.loads(urlopen(request, timeout=600).read().decode('utf-8'))

if response.get('status') == 'finished':
    sys.exit(0)
else:
    sys.exit(1)

# pylama:ignore=E402
