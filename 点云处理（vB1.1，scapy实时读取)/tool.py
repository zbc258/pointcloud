import struct
import ctypes
def shex2sint(data):
	if data[0] in (0,8):
		dec_data = int(data, 16)
	else:
		width = len(data)*4
		dec_data = int(data, 16)		
		if dec_data > 2 ** (width - 1) - 1:
			dec_data = 2 ** width - dec_data
		dec_data = 0 - dec_data
	return dec_data



def hex2bin(x):
	y=format(int(x,16),'b')
	#��ʹ��int���ַ����е�ʮ��������תΪʮ����������ʹ��format����תΪ��������
	#��ʹ��bin��������Ϊ���������0b�Ŀ�ͷ������Ҫʹ��stripȥ����Ӱ��Ч��
	y1=(y.zfill(len(y)-len(y)%4+4) if len(y)%4!=0 else y)
	#ת�����Ķ���������ʡ����ǰ���0����˻ᵼ���ַ����޷����룬��Ҫ�ж�ʲôʱ��ʡ����ǰ���0������
	return y1
def bin2dec_32float(x):

	sign =( -1 if x[0]=='1' else 1)#Ϊ����λ��ֵ
	mi = 2 ** (int(x[1:9], 2)-127)
	xiao = 1
	for num,i in enumerate(x[9:]):
		if i == '1':
			xiao = 2**(-(num+1)) + xiao
	return round(sign * mi * xiao,4)
def hex_to_float(h):
	i = int(h,16)
	cp = ctypes.pointer(ctypes.c_int(i))
	fp = ctypes.cast(cp,ctypes.POINTER(ctypes.c_float))
	return fp.contents.value
def hex2float(h):
    i = int(h,16)
    return struct.unpack('<f',struct.pack('<I', i))[0]



