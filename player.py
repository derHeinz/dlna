#!/usr/bin/python3
# -*- coding: utf-8 -*-

from . dlna_helper import XML_HEADER, create_header, send_request

class Player():

    # http://www.upnp.org/specs/av/UPnP-av-AVTransport-v3-Service-20101231.pdf
    # http://upnp.org/specs/av/UPnP-av-ContentDirectory-v4-Service.pdf
    # http://upnp.org/specs/av/UPnP-av-AVDataStructureTemplate-v1.pdf
    # http://www.upnp.org/specs/av/UPnP-av-ContentDirectory-v1-Service.pdf
    # https://developer.sony.com/develop/audio-control-api/get-started/play-dlna-file#tutorial-step-3
    META_DATA = '''
    <DIDL-Lite xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/" xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dlna="urn:schemas-dlna-org:metadata-1-0/" xmlns:sec="http://www.sec.co.kr/" xmlns:pv="http://www.pv.com/pvns/">
        <item id="{id}" restricted="1">
            <upnp:class>object.item.audioItem.musicTrack</upnp:class>
            <dc:title>{title}</dc:title>
        </item>
    </DIDL-Lite>
    '''
    
    # play should get the variable: speed
    PLAY_BODY =       XML_HEADER + '<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><u:Play xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Speed>1</Speed></u:Play></s:Body></s:Envelope>'
    PAUSE_BODY =      XML_HEADER + '<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><u:Pause xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID></u:Pause></s:Body></s:Envelope>'
    STOP_BODY =       XML_HEADER + '<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><u:Stop xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID></u:Stop></s:Body></s:Envelope>'
    POS_INFO_BODY =   XML_HEADER + '<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><u:GetPositionInfo xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID></u:GetPositionInfo></s:Body></s:Envelope>'
    TRANS_INFO_BODY = XML_HEADER + '<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><u:GetTransportInfo xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID></u:GetTransportInfo></s:Body></s:Envelope>'
    # should get the variabl: url and metadata
    PREPARE_BODY =    XML_HEADER + '<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><CurrentURI>{url}</CurrentURI><CurrentURIMetaData>{metadata}</CurrentURIMetaData></u:SetAVTransportURI></s:Body></s:Envelope>'
    PREPARE_BODY_2 =  XML_HEADER + '<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><CurrentURI>{url}</CurrentURI></u:SetAVTransportURI></s:Body></s:Envelope>'
    
    # should get the variabl: url and metadata
    PREPARE_NEXT_BODY = '<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><u:SetAVTransportURI xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><NextURI>{url}</NextURI><NextURIMetaData>{metadata}</NextURIMetaData></u:SetAVTransportURI></s:Body></s:Envelope>'
    
    def __init__(self, renderer):
        self._renderer = renderer
        
    def stop(self):
        body = self.STOP_BODY
        self._send_request('Stop', body)
        
    def pause(self):
        body = self.PAUSE_BODY
        self._send_request('Pause', body)
        
    def play(self, url_to_play, **kwargs):
        # prepare metadata
        encoded_meta = ''
        if (self._renderer.include_metadata()):
            if ('metadata' in kwargs):
                prepared_metadata = kwargs['metadata']
                encoded_meta = self._escape(prepared_metadata)
            else:
                prepared_metadata = self.META_DATA.format(id=kwargs['title'], title=kwargs['title'])
                encoded_meta = self._escape(prepared_metadata)
        #urllib.parse.quote(meta)
        prepare_body = self.PREPARE_BODY.format(url=url_to_play, metadata=encoded_meta)
        self._send_request('SetAVTransportURI', prepare_body)
        
        #play SOAP message
        play_body = self.PLAY_BODY
        self._send_request('Play', play_body)
        
    def _escape(self, str):
        str = str.replace(b"&", b"&amp;")
        str = str.replace(b"<", b"&lt;")
        str = str.replace(b">", b"&gt;")
        str = str.replace(b"\"", b"&quot;")
        return str
        
    def position_info(self):
        body = self.POS_INFO_BODY
        self._send_request('GetPositionInfo', body)
        
    def transport_info(self):
        body = self.TRANS_INFO_BODY
        self._send_request('GetTransportInfo', body)
        
    def _send_request(self, header_keyword, body):
        device_url = self._renderer.get_url()
        header = create_header('AVTransport', header_keyword)
        send_request(device_url, header, body)
        