import struct
import ctypes
import open3d as o3d
import numpy as np
import math
import scapy
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


def hex2bin(x):
	y=format(int(x,16),'b')
	#先使用int将字符串中的十六进制数转为十进制数，再使用format方法转为二进制数
	#不使用bin函数，因为处理后会带有0b的开头，还需要使用strip去除，影响效率
	y1=(y.zfill(len(y)-len(y)%4+4) if len(y)%4!=0 else y)
	#转换出的二进制数会省略最前面的0，因此会导致字符串无法对齐，需要判断什么时候省略了前面的0并补上
	return y1
def bin2dec_32float(x):

	sign =( -1 if x[0]=='1' else 1)#为符号位赋值
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
def set_label(ax):#设置标签名称
	

	ax.set_zlabel('Z')
	ax.set_ylabel('Y')
	ax.set_xlabel('X')
   
	ax.set_xlim3d(0,120)

	ax.set_ylim3d(-60,60)

	ax.set_zlim3d(0,120)

def point_to_pcd(point):
	pcd = o3d.geometry.PointCloud()
	pcd.points = o3d.utility.Vector3dVector(point)
	return pcd
def pcd_to_point(pcd):
	point=np.asarray(pcd.points)
	return point


def xyzpoints(data_list,point):
	data_str = "".join(data_list)
	# 集群消息参考
	service_id = "0000"
	method_id = "0150"  # 通信协议显示，集群帧的method-ID为0336，转换为十六进制为0150
	length = "00008a00"  # 十进制35328，为长度length；
	heard = service_id + method_id + length
	some_ip_heard = "0000" + "0000" + "01" + "01" + "02" + "00"
	str_refer = heard + some_ip_heard
	all_index = [r.span() for r in scapy.re.finditer(str_refer, data_str)]
	# 索引形式[(3, 5), (9, 11), (13, 15), (15, 17)]
	if all_index == []:
		print("无集群帧")
	else:

		for tuple_index in all_index:

			start_idx_detnList = tuple_index[1] + 20 * 2  # 集群信息起始位置
			start_idx_detns = start_idx_detnList + 65 * 2  # 具体到每一个点
			start_num = start_idx_detnList + 117 * 2 + 799 * 44 * 2
			start_idx_az_ang_corr = start_idx_detnList + 121 * 2 + 799 * 44 * 2
			start_idx_el_ang_corr = start_idx_detnList + 125 * 2 + 799 * 44 * 2


			number_points = int(data_str[start_num: start_num+8], 16)

			az_ang_corr =  hex_to_float(data_str[start_idx_az_ang_corr: start_idx_az_ang_corr + 4 * 2])
			el_ang_corr =  hex_to_float(data_str[start_idx_el_ang_corr: start_idx_el_ang_corr + 4 * 2])

			if  number_points != 0:  # 检查点云个数
				for i in range(0, number_points):
					start_idx = start_idx_detns + i * 44 * 2  # 集群帧中每个点信息占44字节
					flags_idx = start_idx + 8 * 2
					flags = int(data_str[flags_idx:flags_idx + 1 * 2], 16)
					if flags == 0:  # 标志位全0，表示该点有效
						az_ang_idx = start_idx  # 以方位角在数据包中的位置作为起始参考点
						el_ang_idx = start_idx + 9 * 2  # 俯仰角在方位角后9个字节处
						r_idx = start_idx + 17 * 2  # 半径在方位角后17字节处
						v_idx = start_idx + 25 * 2  # 径向速度在方位角后25字节处
						rcs_idx = start_idx + 33 * 2  # RCS在方位角后33字节处
						pbty_idx = start_idx + 36 * 2
						az_ang =  hex_to_float(data_str[az_ang_idx: az_ang_idx + 4 * 2])
						el_ang =  hex_to_float(data_str[el_ang_idx: el_ang_idx + 4 * 2])
						r =  hex_to_float(data_str[r_idx: r_idx + 4 * 2])
						v =  hex_to_float(data_str[v_idx:v_idx + 4 * 2])
						rcs =  hex_to_sint(data_str[rcs_idx: rcs_idx + 1 * 2])
						pbty =  hex_to_sint(data_str[pbty_idx:pbty_idx + 1 * 2])

						x = math.cos(az_ang + az_ang_corr) * (math.cos(el_ang + el_ang_corr) * r)
						y = math.sin(az_ang + az_ang_corr) * (math.cos(el_ang + el_ang_corr) * r)
						z = math.sin(el_ang + el_ang_corr) * r

						if rcs > 2 and r != 0 and pbty > 90 and abs(v) < 0.03:
							point = np.vstack([point, [x, y, z]])
					# print(f'第{i}个点的坐标为（{x},{y},{z}），速度为{v}，RCS值为{rcs}')

	return point


