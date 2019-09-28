#!/usr/bin/python3
# -*- coding: utf-8 -*-
from urllib.request import urlopen, Request

XML_HEADER = '<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n'
NAMESPACE_DC = 'http://purl.org/dc/elements/1.1/'
NAMESPACE_UPNP = 'urn:schemas-upnp-org:metadata-1-0/upnp/'
NAMESPACE_DIDL = 'urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/'

def create_header(type, method):
    soapaction = '"urn:schemas-upnp-org:service:{t}:1#{m}"'.format(t=type,m=method)
    header = {"Content-type":'text/xml; charset="utf-8"',
        "Soapaction": soapaction,
        "Connection": "close",
        "Accept": "text/html, image/gif, image/jpeg, *; q=.2, */*; q=.2",
        "USER-AGENT": "Python/3.7 dlna.py/0.1 UPnP/1.0"
    }
    return header
        
def send_request(url, header, body):
    req = Request(url, body.encode('utf-8'), header)
    response = urlopen(req)
    response_str = response.read()
    return response_str