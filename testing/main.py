import ctypes as c
import itertools
import sys
from time import sleep
from os import environ
from os.path import exists
import usb.core
import usb.util


from usb.backend import libusb0

from usb_def import (MSC_CLASS,
                     CDC_CLASS,
                     CDC_DATA)

###########################################
# Definitions
###########################################
DATA_SHEET_DIR = './data_sheets/'
CONFIGS_DATA_SHEET = '{}config_data_sheet.txt'.format(DATA_SHEET_DIR)
DEMO_CONFIGS_DATA_SHEET = '{}demo_config_data_sheet.txt'.format(DATA_SHEET_DIR)
CONFIGS_RESULTS_SHEET = '{}configs_results.txt'.format(DATA_SHEET_DIR)
BULK_FILE = '{}bulk_data.txt'.format(DATA_SHEET_DIR)
TINY_BULK_FILE = '{}tiny_bulk_data.txt'.format(DATA_SHEET_DIR)
BAD_TINY_BULK_FILE = '{}bad_tiny_bulk_data.txt'.format(DATA_SHEET_DIR)
BULK_RESULTS_SHEET = '{}bulk_results.txt'.format(DATA_SHEET_DIR)
TEMP = '{}temp.txt'.format(DATA_SHEET_DIR)

PASS_MARK = '[0]'
FAIL_MARK = '[X]'
MISSING_MARK = '[M]'
NEUTRAL_MARK = ' - '

CONFIGURATION = 'Configuration:'
INTERFACE = 'Interface:'
ENDPOINT = 'Endpoint:'
HEADER_SPACE      = '    '
DETAIL_SPACE      = '  '
CFG_HEADER        = '{}{}\n'.format(HEADER_SPACE*0, CONFIGURATION)
CFG_DETAIL_SPACE  = HEADER_SPACE*0 + DETAIL_SPACE
INTF_HEADER       = '{}{}\n'.format(HEADER_SPACE*1, INTERFACE)
INTF_DETAIL_SPACE = HEADER_SPACE*1 + DETAIL_SPACE
EP_HEADER         = '{}{}\n'.format(HEADER_SPACE*2, ENDPOINT)
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

def find_intf_class(cfg, cls=MSC_CLASS):
    intf = usb.util.find_descriptor(cfg, bInterfaceClass=cls)
    assert intf is not None
    return intf

def find_bulk_out(e):
    return usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT

def find_bulk_in(e):
    return usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN

def read_chunk(file, size):
    while True:
        data = file.read(size)
        if not data:
            break
        yield data

def read_configs_sheet(f_name=DEMO_CONFIGS_DATA_SHEET):
    assert exists(f_name)
    cfgs = []
    current_descr = None
    with open(f_name, 'r') as file_in:
        for l in file_in:
            line = l.rstrip().lstrip()
            if line == CONFIGURATION:
                cfgs.append({'intf':[]})
                current_descr = cfgs[-1]
            elif line == INTERFACE:
                cfgs[-1]['intf'].append({'ep':[]})
                current_descr = cfgs[-1]['intf'][-1]
            elif line == ENDPOINT:
                cfgs[-1]['intf'][-1]['ep'].append(dict())
                current_descr = cfgs[-1]['intf'][-1]['ep'][-1]
            else:
                if '=' in line:
                    field, v = line.split('=')
                    try:
                        value = int(v)
                    except ValueError:
                        value = v
                    current_descr[field] = value
    return cfgs

def write_configs_sheet(configs, f_name=CONFIGS_DATA_SHEET):
    with open(f_name, 'wb') as f_out:
        for cfg in configs:
            f_out.write(CFG_HEADER)
            for field, value in cfg.items():
                if field != 'intf':
                    f_out.write('{}{}={}\n'.format(CFG_DETAIL_SPACE, field, value))
            for intf in cfg['intf']:
                f_out.write(INTF_HEADER)
                for field, value in intf.items():
                    if field != 'ep':
                        f_out.write('{}{}={}\n'.format(INTF_DETAIL_SPACE, field, value))
                for ep in intf['ep']:
                    f_out.write(EP_HEADER)
                    for field, value in ep.items():
                        f_out.write('{}{}={}\n'.format(EP_DETAIL_SPACE, field, value))

def read_configs_dev(dev=dev):
    configs = []
    for cfg in dev:
        cfg_dict = dict()
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
            intf_dict = dict()
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
                ep_dict = dict()
                ep_dict['bLength'] = ep.bLength
                ep_dict['bDescriptorType'] = ep.bDescriptorType
                ep_dict['bEndpointAddress'] = ep.bEndpointAddress
                ep_dict['bmAttributes'] = ep.bmAttributes
                ep_dict['wMaxPacketSize'] = ep.wMaxPacketSize
                ep_dict['bInterval'] = ep.bInterval
                intf_dict['ep'].append(ep_dict)
            cfg_dict['intf'].append(intf_dict)
        configs.append(cfg_dict)
    return configs

# TODO: Swap interfaces being compared if comparison fails
def compare_configs(act_configs, exp_configs, f_name=CONFIGS_RESULTS_SHEET):
    with open(f_name, 'wb') as f_out:
        for idx, cfg in enumerate(act_configs):
            if len(exp_configs) >= idx + 1:
                cur_exp_cfg = exp_configs[idx]
                f_out.write('{}{}'.format(NEUTRAL_MARK, CFG_HEADER))
            else:
                cur_exp_cfg = {'intf' : []}
                f_out.write('{}{}'.format(MISSING_MARK, CFG_HEADER))
            for field in cfg:
                if field != 'intf':
                    if field not in cur_exp_cfg:
                        f_out.write('{}{}{}={} / None\n'.format(MISSING_MARK, CFG_DETAIL_SPACE, field, cfg[field]))
                    elif cfg[field] != cur_exp_cfg[field]:
                        f_out.write('{}{}{}={} / {}={}\n'.format(FAIL_MARK, CFG_DETAIL_SPACE, field, cfg[field], field, cur_exp_cfg[field]))
                    else:
                        f_out.write('{}{}{}={} / {}={}\n'.format(PASS_MARK, CFG_DETAIL_SPACE, field, cfg[field], field, cur_exp_cfg[field]))
            for idx, intf in enumerate(cfg['intf']):
                if len(cur_exp_cfg['intf']) >= idx + 1:
                    cur_exp_intf = cur_exp_cfg['intf'][idx]
                    f_out.write('{}{}'.format(NEUTRAL_MARK, INTF_HEADER))
                else:
                    cur_exp_intf = {'ep' : []}
                    f_out.write('{}{}'.format(MISSING_MARK, INTF_HEADER))
                for field in intf:
                    if field != 'ep':
                        if field not in cur_exp_intf:
                            f_out.write('{}{}{}={} / None\n'.format(MISSING_MARK, INTF_DETAIL_SPACE, field, intf[field]))
                        elif intf[field] != cur_exp_intf[field]:
                            f_out.write('{}{}{}={} / {}={}\n'.format(FAIL_MARK, INTF_DETAIL_SPACE, field, intf[field], field, cur_exp_intf[field]))
                        else:
                            f_out.write('{}{}{}={} / {}={}\n'.format(PASS_MARK, INTF_DETAIL_SPACE, field, intf[field], field, cur_exp_intf[field]))
                for idx, ep in enumerate(intf['ep']):
                    if len(cur_exp_intf['ep']) >= idx + 1:
                        cur_exp_ep = cur_exp_intf['ep'][idx]
                        f_out.write('{}{}'.format(NEUTRAL_MARK, EP_HEADER))
                    else:
                        cur_exp_ep = dict()
                        f_out.write('{}{}'.format(MISSING_MARK, EP_HEADER))
                    for field in ep:
                        if field not in cur_exp_ep:
                            f_out.write('{}{}{}={} / None\n'.format(MISSING_MARK, EP_DETAIL_SPACE, field, ep[field]))
                        elif ep[field] != cur_exp_ep[field]:
                            f_out.write('{}{}{}={} / {}={}\n'.format(FAIL_MARK, EP_DETAIL_SPACE, field, ep[field], field, cur_exp_ep[field]))
                        else:
                            f_out.write('{}{}{}={} / {}={}\n'.format(PASS_MARK, EP_DETAIL_SPACE, field, ep[field], field, cur_exp_ep[field]))

def stream_file(cfg, f_name=TINY_BULK_FILE):
    intf = find_intf_class(cfg, CDC_CLASS)
    endpoint_out = usb.util.find_descriptor(intf, custom_match=find_bulk_out)
    endpoint_in = usb.util.find_descriptor(intf, custom_match=find_bulk_in)
    assert endpoint_out is not None
    assert endpoint_in is not None
    out_buff = ''
    in_buff = ''
    with open(f_name, 'rb') as f_in:
        for data in read_chunk(f_in, endpoint_out.wMaxPacketSize):
            assert endpoint_out.write(data) == len(data)
            out_buff += data
            in_buff += endpoint_in.read(len(data))
    return out_buff, in_buff

def compare_buffs(out_buff, in_buff, f_name=BULK_RESULTS_SHEET):
    out_lines = out_buff.split('\n')
    in_lines = in_buff.split('\n')
    with open(f_name, 'wb') as f_out:
        for idx, (out_line, in_line) in enumerate(itertools.izip(out_lines, in_lines), 1):
            if out_line != in_line:
                f_out.write('{ln}:{incorrect} {o}\n{ln}:{neutral} {i}\n'.format(ln=idx, incorrect=FAIL_MARK, neutral=NEUTRAL_MARK, o=out_line, i=in_line))
            else:
                f_out.write('{ln}:{passing} {o}\n'.format(ln=idx, passing=PASS_MARK, o=out_line))


def init(idVendor=0xcafe, idProduct=0x0001):
    # set environment
    environ['PYUSB_DEBUG'] = 'debug'
    # find our device
    be = libusb0.get_backend()
    _dev = usb.core.find(idVendor=idVendor, idProduct=idProduct, backend=be)
    # was it found?
    if _dev is None:
        raise ValueError('Device not found')
    return _dev

###########################################
# Main
###########################################
dev = init()

act_configs = read_configs_dev(dev)
exp_configs = read_configs_sheet()
compare_configs(act_configs, exp_configs)
write_configs_sheet(act_configs)

dev.set_configuration()
cfg = dev.get_active_configuration()
out_buff, in_buff = stream_file(cfg)
compare_buffs(out_buff, in_buff)

# assert dev.ctrl_transfer(0x40, CTRL_LOOPBACK_WRITE, 0, 0, msg) == len(msg)
# ret_msg = dev.ctrl_transfer(0xC0, CTRL_LOOPBACK_READ, 0, 0, len(msg))
# sret = ''.join([chr(x) for x in ret_msg])
# assert sret == msg
