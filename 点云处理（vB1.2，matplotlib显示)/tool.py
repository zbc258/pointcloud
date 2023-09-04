import struct
import ctypes
import matplotlib.pyplot as plt
def set_label(ax):#设置标签名称
    #ax.cla()

    ax.set_zlabel('Z')
    ax.set_ylabel('Y')
    ax.set_xlabel('X')
   
    ax.set_xlim3d(0,120)

    ax.set_ylim3d(-60,60)

    #ax.set_zlim3d(0,20)
def hex_to_float(h):
	i = int(h,16)
	cp = ctypes.pointer(ctypes.c_int(i))
	fp = ctypes.cast(cp,ctypes.POINTER(ctypes.c_float))
	return fp.contents.value
def hex2float(h):
	i = int(h,16)
	return struct.unpack('<f',struct.pack('<I', i))[0]

def hex_to_sint(data):
	# 把16进制字符串转成带符号10进制

	if data[0] in '01234567':
		dec_data = int(data, 16)
	else:
		width = 8
		dec_data = int(data, 16)
		if dec_data > 2 ** (width - 1) - 1:
			dec_data = 2 ** width - dec_data
		dec_data = 0 - dec_data

	
	return dec_data

