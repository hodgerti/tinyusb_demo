import usb.core
import usb.util

from usb.backend import libusb1

# find our device
be = libusb1.get_backend()
dev = usb.core.find(idVendor=0xcaff, idProduct=0x0001, backend=be)

# was it found?
if dev is None:
    raise ValueError('Device not found')

# set the active configuration. With no arguments, the first
# configuration will be the active one
dev.set_configuration()

# get an endpoint instance
cfg = dev.get_active_configuration()
intf = cfg[(0,0)]

ep = usb.util.find_descriptor(
    intf,
    # match the first OUT endpoint
    custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)

assert ep is not None

# write the data
ep.write('test')

# bLength 1 12h
# bDescriptorType 1 01h Device
# bcdUSB 2 0200h USB Spec 2.0
# bDeviceClass 1 EFh Miscellaneous
# bDeviceSubClass 1 02h Common Class
# bDeviceProtocol 1 01h Interface Association Descriptor
# bMaxPacketSize0 1 40h 64 bytes
# idVendor 2 CAFEh
# idProduct 2 0001h  #
# bcdDevice 2 0100h 1.00
# iManufacturer 1 01h "tinyusb.org"
# iProduct 1 02h "tinyusb device"
# iSerialNumber 1 03h "123456"
# bNumConfigurations 1 01h
