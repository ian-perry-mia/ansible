#!/usr/bin/env python3
import requests
import logging
import socket
import sys
import argparse
import pprint

parser = argparse.ArgumentParser()

parser.add_argument('-d', '--debug', help='Enables debugging output', action='store_true')
parser.add_argument('-i', '--ip', help='IP address to set in DNS', required=True)

args = parser.parse_args()

logger = logging.getLogger(__name__)

if args.debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

base_url = 'http://hq-dns1.hq.avionics411.com'
base_port = '8081'
url = f'{base_url}:{base_port}/api/v1'
server_name = 'localhost'
domain = 'hq.avionics411.com'

req = requests.Session()

req.headers.update({'X-Api-Key': 'PWEPVSjHmVP57YgiSrZPJxBlmX2DRioo'})

resp = req.get(f'{url}/servers/{server_name}/zones')
if not resp.ok:
    logger.fatal("Unable to retrieve list of zones: <%s> - %s", resp.status_code, resp.text)

logger.debug(pprint.pformat(resp.json()))

zones = resp.json()

zone = [z for z in zones if z['id'] == f'{domain}.']
zone = zone[0]

reverse_zone = args.ip.split('.')[0:3]
reverse_zone.reverse()
reverse_zone = '.'.join(reverse_zone)
reverse_zone = f'{reverse_zone}.in-addr.arpa.'

rzone = [z for z in zones if z['id'] == reverse_zone]
rzone = rzone[0]
if len(rzone) == 0:
    logger.info('Reverse zone does not exist, creating...')
    data = {
        'name': rzone,
        'kind': 'Native',
        'masters': [],
        'nameservers': []
    }

url = f'{base_url}:{base_port}' + zone['url']

resp = req.get(url)
if not resp.ok:
    logger.fatal("Unable to retrieve zone information: <%s> - %s", resp.status_code, resp.text)

logger.debug(pprint.pformat(resp.json()))

for rrset in resp.json()['rrsets']:
    if rrset['name'] == f'{socket.gethostname()}.{domain}':
        logger.info("Record already exists, exiting...")
        sys.exit(0)
    for record in rrset['records']:
        if record['content'] == args.ip:
            logger.fatal("IP address already exists in database.")
            sys.exit(0)
    
logger.info("No matching record, creating...")
obj = {
    'rrsets': [{
        'comments': [],
        'name': f'{socket.gethostname()}.{domain}.',
        'records': [{'content': args.ip, 'disabled': False}],
        'ttl': 3600,
        'type': 'A',
        'changetype': 'REPLACE'
    }]
}

resp = req.patch(url, json = obj)
logger.debug(resp.request.url)
logger.debug(resp.request.body)
logger.debug(resp.request.headers)
if not resp.ok:
    logger.fatal("Unable to add record to DNS Server: <%s> - %s", resp.status_code, resp.text)
    sys.exit(1)
logger.info("Successfully added record.")

