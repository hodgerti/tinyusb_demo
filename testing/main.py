from collections import OrderedDict
import sys
from os import environ
import usb.core
import usb.util

from usb.backend import libusb1

###########################################
# Definitions
###########################################
CONFIGS_DATA_SHEET = './config_data_sheet.txt'

HEADER_SPACE      = '    '
DETAIL_SPACE      = '  '
CFG_HEADER        = '{}Configuration:\n'.format(HEADER_SPACE*0)
CFG_DETAIL_SPACE  = HEADER_SPACE*0 + DETAIL_SPACE
INTF_HEADER       = '{}Interface:\n'.format(HEADER_SPACE*1)
INTF_DETAIL_SPACE = HEADER_SPACE*1 + DETAIL_SPACE
EP_HEADER         = '{}Endpoint:\n'.format(HEADER_SPACE*2)
EP_DETAIL_SPACE   = HEADER_SPACE*2 + DETAIL_SPACE

###########################################
# Global Variables
###########################################
dev = None

###########################################
# Functions
###########################################
def string_to_hex(s):
    s_ = hex(int(s))
    # if len(s_)%2 != 0:
    #     s_ += '0'
    return s_

def init(idVendor=0xcafe, idProduct=0x0001):
    # set environment
    environ['PYUSB_DEBUG'] = 'debug'
    # find our device
    be = libusb1.get_backend()
    _dev = usb.core.find(idVendor=idVendor, idProduct=idProduct, backend=be)
    # was it found?
    if _dev is None:
        raise ValueError('Device not found')
    return _dev

def write_configs(configs, f_name=CONFIGS_DATA_SHEET):
    f_out = open(f_name, 'wb')
    for cfg in configs:
        f_out.write(CFG_HEADER)
        for field, value in cfg.items():
            if field != 'intf':
                f_out.write('{}{}={}\n'.format(CFG_DETAIL_SPACE, field, string_to_hex(value)))
        for intf in cfg['intf']:
            f_out.write(INTF_HEADER)
            for field, value in intf.items():
                if field != 'ep':
                    f_out.write('{}{}={}\n'.format(INTF_DETAIL_SPACE, field, string_to_hex(value)))
            for ep in intf['ep']:
                f_out.write(EP_HEADER)
                for field, value in ep.items():
                    f_out.write('{}{}={}\n'.format(EP_DETAIL_SPACE, field, string_to_hex(value)))
    f_out.close()


def record_config(dev=dev, f_name=CONFIGS_DATA_SHEET):
    configs = []
    for cfg in dev:
        cfg_dict = OrderedDict()
        cfg_dict['bLength'] = cfg.bLength
        cfg_dict['bDescriptorType'] = cfg.bDescriptorType
        cfg_dict['wTotalLength'] = cfg.wTotalLength
        cfg_dict['bNumInterfaces'] = cfg.bNumInterfaces
        cfg_dict['bConfigurationValue'] = cfg.bConfigurationValue
        cfg_dict['iConfiguration'] = cfg.iConfiguration
        cfg_dict['bmAttributes'] = cfg.bmAttributes
        cfg_dict['bMaxPower'] = cfg.bMaxPower
        cfg_dict['intf'] = []
        for intf in cfg:
            intf_dict = OrderedDict()
            intf_dict['bLength'] = intf.bLength
            intf_dict['bDescriptorType'] = intf.bDescriptorType
            intf_dict['bInterfaceNumber'] = intf.bInterfaceNumber
            intf_dict['bAlternateSetting'] = intf.bAlternateSetting
            intf_dict['bNumEndpoints'] = intf.bNumEndpoints
            intf_dict['bInterfaceClass'] = intf.bInterfaceClass
            intf_dict['bInterfaceSubClass'] = intf.bInterfaceSubClass
            intf_dict['bInterfaceProtocol'] = intf.bInterfaceProtocol
            intf_dict['iInterface'] = intf.iInterface
            intf_dict['ep'] = []
            for ep in intf:
                ep_dict = OrderedDict()
                ep_dict['bLength'] = ep.bLength
                ep_dict['bDescriptorType'] = ep.bDescriptorType
                ep_dict['bEndpointAddress'] = ep.bEndpointAddress
                ep_dict['bmAttributes'] = ep.bmAttributes
                ep_dict['wMaxPacketSize'] = ep.wMaxPacketSize
                ep_dict['bInterval'] = ep.bInterval
                intf_dict['ep'].append(ep_dict)
            cfg_dict['intf'].append(intf_dict)
        configs.append(cfg_dict)
    write_configs(configs)
    return configs

###########################################
# Main
###########################################
dev = init()
configs = record_config(dev)

# dev.set_configuration(5)
# cfg = util.find_descriptor(dev, bConfigurationValue=5)
# cfg.set()

dev.set_configuration()
cfg = dev.get_active_configuration()

def ep_is_out(ep):
    return usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_OUT

def interface_has_out_endpoint(intf):
    for ep in intf:
        if ep_is_out(ep):
            return True


# intf = usb.util.find_descriptor(dev, bInterfaceNumber=???)
# dev.set_interface_altsetting(intf) / intf.set_altsetting()
intf = usb.util.find_descriptor(cfg, custom_match=interface_has_out_endpoint)

# assert dev.ctrl_transfer(0x40, CTRL_LOOPBACK_WRITE, 0, 0, msg) == len(msg)
# ret_msg = dev.ctrl_transfer(0xC0, CTRL_LOOPBACK_READ, 0, 0, len(msg))
# sret = ''.join([chr(x) for x in ret_msg])
# assert sret == msg

ep = usb.util.find_descriptor(intf, custom_match=ep_is_out)

assert ep is not None

# write the data
msg = 'test'
assert len(dev.write(1, msg, 100)) == len(msg)
