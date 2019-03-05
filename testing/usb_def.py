import ctypes as c

CDC_CLASS = 0x02
MSC_CLASS = 0x08
CDC_DATA  = 0x0A

# class endpoint_descriptor(c.Structure):
#     _pack_ = 1
#     _fields_ = [("bLength", c.c_ubyte*7)]