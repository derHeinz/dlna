#!/usr/bin/python3
# -*- coding: utf-8 -*-
import uuid
import xml.etree.ElementTree as ET

from . dlna_helper import XML_HEADER, create_header, send_request


class Player():

    # http://www.upnp.org/specs/av/UPnP-av-AVTransport-v3-Service-20101231.pdf
    # http://upnp.org/specs/av/UPnP-av-ContentDirectory-v4-Service.pdf
    # http://upnp.org/specs/av/UPnP-av-AVDataStructureTemplate-v1.pdf
    # http://www.upnp.org/specs/av/UPnP-av-ContentDirectory-v1-Service.pdf
    # https://developer.sony.com/develop/audio-control-api/get-started/play-dlna-file#tutorial-step-3
    META_DATA = '''
    <DIDL-Lite xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/" 
    xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/" 
    xmlns:dc="http://purl.org/dc/elements/1.1/" 
    xmlns:dlna="urn:schemas-dlna-org:metadata-1-0/" 
    xmlns:sec="http://www.sec.co.kr/" 
    xmlns:pv="http://www.pv.com/pvns/">
        <item id="{id}" parentID="{parentid}" restricted="1">
            <dc:title>{title}</dc:title>

            <dc:creator>{artist}</dc:creator>
            <upnp:artist>{artist}</upnp:artist>
            <upnp:actor>{artist}</upnp:actor>
            <upnp:author>{artist}</upnp:author>
            
            <upnp:class>object.item.audioItem.musicTrack</upnp:class>
            {res}
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
        return self._send_request('Stop', body)

    def pause(self):
        body = self.PAUSE_BODY
        return self._send_request('Pause', body)

    def play(self, url_to_play, **kwargs):
        # prepare metadata
        encoded_meta = ''
        if (self._renderer.include_metadata()):
            if ('item' in kwargs):
                # uses mediaserver's item
                item = kwargs['item']
                prepared_metadata = self.META_DATA.format(id=uuid.uuid4(), parentid=uuid.uuid4(), title=item.get_title(), artist=item.get_actor(), res=item.get_res_as_string())
                encoded_meta = self._escape(self._clean(prepared_metadata))
            elif ('metadata_raw' in kwargs):
                encoded_meta = kwargs['metadata_raw']
        # urllib.parse.quote(meta)
        prepare_body = self.PREPARE_BODY.format(url=url_to_play, metadata=encoded_meta)
        self._send_request('SetAVTransportURI', prepare_body)

        # play SOAP message
        play_body = self.PLAY_BODY
        return self._send_request('Play', play_body)

    def _escape(self, str):
        str = str.replace("&", "&amp;")
        str = str.replace("<", "&lt;")
        str = str.replace(">", "&gt;")
        return str

    def _clean(self, str):
        result = str.strip()
        result = " ".join(result.split())
        return result

    def position_info(self):
        response = self._send_request('GetPositionInfo', self.POS_INFO_BODY)
        xml_content = ET.fromstring(response.read().decode('utf-8'))
        getPositionInfoResponse = xml_content.find(".//{urn:schemas-upnp-org:service:AVTransport:1}GetPositionInfoResponse")
        result = {}

        for child in getPositionInfoResponse:
            result[child.tag] = child.text

        return result

    def transport_info(self):
        response = self._send_request('GetTransportInfo', self.TRANS_INFO_BODY)
        xml_content = ET.fromstring(response.read().decode('utf-8'))
        getPositionInfoResponse = xml_content.find(".//{urn:schemas-upnp-org:service:AVTransport:1}GetTransportInfoResponse")
        result = {}

        for child in getPositionInfoResponse:
            result[child.tag] = child.text

        return result

    def _send_request(self, header_keyword, body):
        device_url = self._renderer.get_url()
        header = create_header('AVTransport', header_keyword)
        return send_request(device_url, header, body)
