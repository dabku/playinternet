import requests
import xml.etree.ElementTree as ET
from enum import Enum
import logging
import sys
import traceback

class PlayHuaweiB525:
    def __init__(self, ip):
        self.ip = ip
        self.seesion = None
        self.set_session()

    def set_session(self):
        logging.debug('Setting session')
        r = requests.get("http://{}/api/webserver/SesTokInfo".format(self.ip))
        xml_root = ET.fromstring(r.text)
        _ = xml_root.find('TokInfo').text
        self.seesion = xml_root.find('SesInfo').text

    def get_statistics(self):
        logging.debug('Getting monthly statistics')
        r = requests.get("http://{}/api/monitoring/month_statistics".format(self.ip))
        xml_root = ET.fromstring(r.text)
        api_data = {child.tag: child.text for child in xml_root}
        return api_data

    def get_signal_status(self):
        logging.debug('Getting signal status')
        r = requests.get("http://{}/api/monitoring/status".format(self.ip),
                         headers={'Cookie': 'SessionID=' + self.seesion})

        xml_root = ET.fromstring(r.text)

        api_data = {child.tag: child.text for child in xml_root}
        evaluated_network = NetworkType.get(api_data.get('CurrentNetworkTypeEx'), api_data.get('CurrentNetworkType'))
        api_data.update({'EvaluatedNetworkType': int(evaluated_network[:-1])})
        return api_data

    def get_traffic(self):
        logging.debug('Getting traffic statistics')
        r = requests.get("http://{}/api/monitoring/traffic-statistics".format(self.ip))
        xml_root = ET.fromstring(r.text)
        api_data = {child.tag: child.text for child in xml_root}
        return api_data

    def get_all(self):
        d = {}
        try:
            d.update(self.get_statistics())
            d.update(self.get_signal_status())
            d.update(self.get_traffic())
        except Exception as e:
            _exc_type, _exc_value, _exc_traceback = sys.exc_info()
            logging.error(traceback.format_exception(_exc_type, _exc_value, _exc_traceback))
        return d


class eNetworkTypes(Enum):
    '''
    refactored from main.js from router web panel
    '''
    MACRO_NET_WORK_TYPE_NOSERVICE = '0'
    MACRO_NET_WORK_TYPE_GSM = '1'
    MACRO_NET_WORK_TYPE_GPRS = '2'
    MACRO_NET_WORK_TYPE_EDGE = '3'
    MACRO_NET_WORK_TYPE_WCDMA = '4'
    MACRO_NET_WORK_TYPE_HSDPA = '5'
    MACRO_NET_WORK_TYPE_HSUPA = '6'
    MACRO_NET_WORK_TYPE_HSPA = '7'
    MACRO_NET_WORK_TYPE_TDSCDMA = '8'
    MACRO_NET_WORK_TYPE_HSPA_PLUS = '9'
    MACRO_NET_WORK_TYPE_EVDO_REV_0 = '10'
    MACRO_NET_WORK_TYPE_EVDO_REV_A = '11'
    MACRO_NET_WORK_TYPE_EVDO_REV_B = '12'
    MACRO_NET_WORK_TYPE_1xRTT = '13'
    MACRO_NET_WORK_TYPE_UMB = '14'
    MACRO_NET_WORK_TYPE_1xEVDV = '15'
    MACRO_NET_WORK_TYPE_3xRTT = '16'
    MACRO_NET_WORK_TYPE_HSPA_PLUS_64QAM = '17'
    MACRO_NET_WORK_TYPE_HSPA_PLUS_MIMO = '18'
    MACRO_NET_WORK_TYPE_LTE = '19'
    MACRO_NET_WORK_TYPE_EX_NOSERVICE = '0'
    MACRO_NET_WORK_TYPE_EX_GSM = '1'
    MACRO_NET_WORK_TYPE_EX_GPRS = '2'
    MACRO_NET_WORK_TYPE_EX_EDGE = '3'
    MACRO_NET_WORK_TYPE_EX_IS95A = '21'
    MACRO_NET_WORK_TYPE_EX_IS95B = '22'
    MACRO_NET_WORK_TYPE_EX_CDMA_1x = '23'
    MACRO_NET_WORK_TYPE_EX_EVDO_REV_0 = '24'
    MACRO_NET_WORK_TYPE_EX_EVDO_REV_A = '25'
    MACRO_NET_WORK_TYPE_EX_EVDO_REV_B = '26'
    MACRO_NET_WORK_TYPE_EX_HYBRID_CDMA_1x = '27'
    MACRO_NET_WORK_TYPE_EX_HYBRID_EVDO_REV_0 = '28'
    MACRO_NET_WORK_TYPE_EX_HYBRID_EVDO_REV_A = '29'
    MACRO_NET_WORK_TYPE_EX_HYBRID_EVDO_REV_B = '30'
    MACRO_NET_WORK_TYPE_EX_EHRPD_REL_0 = '31'
    MACRO_NET_WORK_TYPE_EX_EHRPD_REL_A = '32'
    MACRO_NET_WORK_TYPE_EX_EHRPD_REL_B = '33'
    MACRO_NET_WORK_TYPE_EX_HYBRID_EHRPD_REL_0 = '34'
    MACRO_NET_WORK_TYPE_EX_HYBRID_EHRPD_REL_A = '35'
    MACRO_NET_WORK_TYPE_EX_HYBRID_EHRPD_REL_B = '36'
    MACRO_NET_WORK_TYPE_EX_WCDMA = '41'
    MACRO_NET_WORK_TYPE_EX_HSDPA = '42'
    MACRO_NET_WORK_TYPE_EX_HSUPA = '43'
    MACRO_NET_WORK_TYPE_EX_HSPA = '44'
    MACRO_NET_WORK_TYPE_EX_HSPA_PLUS = '45'
    MACRO_NET_WORK_TYPE_EX_DC_HSPA_PLUS = '46'
    MACRO_NET_WORK_TYPE_EX_TD_SCDMA = '61'
    MACRO_NET_WORK_TYPE_EX_TD_HSDPA = '62'
    MACRO_NET_WORK_TYPE_EX_TD_HSUPA = '63'
    MACRO_NET_WORK_TYPE_EX_TD_HSPA = '64'
    MACRO_NET_WORK_TYPE_EX_TD_HSPA_PLUS = '65'
    MACRO_NET_WORK_TYPE_EX_802_16E = '81'
    MACRO_NET_WORK_TYPE_EX_LTE = '101'
    MACRO_NET_WORK_TYPE_EX_LTE_PLUS = '1011'


class NetworkType:
    '''
    refactored case from main.js from router web panel
    '''
    _2gex = (eNetworkTypes.MACRO_NET_WORK_TYPE_EX_GSM, eNetworkTypes.MACRO_NET_WORK_TYPE_EX_GPRS,
             eNetworkTypes.MACRO_NET_WORK_TYPE_EX_EDGE, eNetworkTypes.MACRO_NET_WORK_TYPE_EX_IS95A,
             eNetworkTypes.MACRO_NET_WORK_TYPE_EX_IS95B, eNetworkTypes.MACRO_NET_WORK_TYPE_EX_CDMA_1x,
             eNetworkTypes.MACRO_NET_WORK_TYPE_EX_HYBRID_CDMA_1x)
    _3gex = (eNetworkTypes.MACRO_NET_WORK_TYPE_EX_EVDO_REV_0, eNetworkTypes.MACRO_NET_WORK_TYPE_EX_EVDO_REV_A,
             eNetworkTypes.MACRO_NET_WORK_TYPE_EX_EVDO_REV_B, eNetworkTypes.MACRO_NET_WORK_TYPE_EX_HYBRID_EVDO_REV_0,
             eNetworkTypes.MACRO_NET_WORK_TYPE_EX_HYBRID_EVDO_REV_A,
             eNetworkTypes.MACRO_NET_WORK_TYPE_EX_HYBRID_EVDO_REV_B, eNetworkTypes.MACRO_NET_WORK_TYPE_EX_EHRPD_REL_0,
             eNetworkTypes.MACRO_NET_WORK_TYPE_EX_EHRPD_REL_A, eNetworkTypes.MACRO_NET_WORK_TYPE_EX_EHRPD_REL_B,
             eNetworkTypes.MACRO_NET_WORK_TYPE_EX_HYBRID_EHRPD_REL_0,
             eNetworkTypes.MACRO_NET_WORK_TYPE_EX_HYBRID_EHRPD_REL_A,
             eNetworkTypes.MACRO_NET_WORK_TYPE_EX_HYBRID_EHRPD_REL_B, eNetworkTypes.MACRO_NET_WORK_TYPE_EX_WCDMA,
             eNetworkTypes.MACRO_NET_WORK_TYPE_EX_HSDPA, eNetworkTypes.MACRO_NET_WORK_TYPE_EX_HSUPA,
             eNetworkTypes.MACRO_NET_WORK_TYPE_EX_HSPA, eNetworkTypes.MACRO_NET_WORK_TYPE_EX_HSPA_PLUS,
             eNetworkTypes.MACRO_NET_WORK_TYPE_EX_DC_HSPA_PLUS, eNetworkTypes.MACRO_NET_WORK_TYPE_EX_TD_SCDMA,
             eNetworkTypes.MACRO_NET_WORK_TYPE_EX_TD_HSDPA, eNetworkTypes.MACRO_NET_WORK_TYPE_EX_TD_HSUPA,
             eNetworkTypes.MACRO_NET_WORK_TYPE_EX_TD_HSPA, eNetworkTypes.MACRO_NET_WORK_TYPE_EX_TD_HSPA_PLUS)
    _4gex = (eNetworkTypes.MACRO_NET_WORK_TYPE_EX_LTE, eNetworkTypes.MACRO_NET_WORK_TYPE_EX_LTE_PLUS)
    _2g = (eNetworkTypes.MACRO_NET_WORK_TYPE_GSM, eNetworkTypes.MACRO_NET_WORK_TYPE_GPRS,
           eNetworkTypes.MACRO_NET_WORK_TYPE_EDGE, eNetworkTypes.MACRO_NET_WORK_TYPE_1xRTT)
    _3g = (eNetworkTypes.MACRO_NET_WORK_TYPE_WCDMA, eNetworkTypes.MACRO_NET_WORK_TYPE_TDSCDMA,
           eNetworkTypes.MACRO_NET_WORK_TYPE_EVDO_REV_0, eNetworkTypes.MACRO_NET_WORK_TYPE_EVDO_REV_A,
           eNetworkTypes.MACRO_NET_WORK_TYPE_EVDO_REV_B, eNetworkTypes.MACRO_NET_WORK_TYPE_HSDPA,
           eNetworkTypes.MACRO_NET_WORK_TYPE_HSUPA, eNetworkTypes.MACRO_NET_WORK_TYPE_HSPA,
           eNetworkTypes.MACRO_NET_WORK_TYPE_HSPA_PLUS, eNetworkTypes.MACRO_NET_WORK_TYPE_HSPA_PLUS_64QAM,
           eNetworkTypes.MACRO_NET_WORK_TYPE_HSPA_PLUS_MIMO)
    _4g = (eNetworkTypes.MACRO_NET_WORK_TYPE_LTE)

    networks = (
        ('4G', _4gex, _4g),
        ('3G', _3gex, _3g),
        ('2G', _2gex, _2g),

    )

    @classmethod
    def get(cls, CurrentNetworkTypeEx, CurrentNetworkType):
        if CurrentNetworkTypeEx:
            for network, values, _ in cls.networks:
                if eNetworkTypes(CurrentNetworkTypeEx) in values:
                    return network
        if CurrentNetworkType:
            for network, _, values in cls.networks:
                if eNetworkTypes(CurrentNetworkType) in values:
                    return network
