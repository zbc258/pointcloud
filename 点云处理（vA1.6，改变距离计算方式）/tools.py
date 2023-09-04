import struct
import open3d as o3d
import numpy as np
#import cupy as cp
import math
import dpkt
import binascii
import socket


def ipheader(header):
	# ヘッダの処理
	src = socket.inet_ntoa(header.src)
	dst = socket.inet_ntoa(header.dst)
	# TCP
	if type(header.data) == dpkt.tcp.TCP:
		print("TCP %s:%s => %s:%s (len:%s)" % (src, header.data.sport, dst, header.data.dport, len(header.data.data)))
	# UDP
	elif type(header.data) == dpkt.udp.UDP:
		print("UDP %s:%s => %s:%s (len:%s)" % (src, header.data.sport, dst, header.data.dport, len(header.data.data)))
	# ICMP
	elif type(header.data) == dpkt.icmp.ICMP:
		print("ICMP %s:type %s,code %s => %s (len:%s)" % (
		src, header.data.type, header.data.code, dst, len(header.data.data)))

	# その他
	else:
		print("%s => %s" % (src, dst))
def determine_type(f):
	# 读取文件的magic字段，读完后还要把文件指针移到0位置
	
	magic_head = f.read(4)
	f.seek(0, 0)
	if magic_head == b'\n\r\r\n':
		pcap  = dpkt.pcapng.Reader(f)
	elif magic_head == b'\xd4\xc3\xb2\xa1':
		pcap  = dpkt.pcap.Reader(f)
	else:
		print("[DEBUG in PcapUtils] 读取的文件既不是pcap也不是pcapng格式")
	#判断读取的文件是pcap还是pcapng格式   
	return pcap

def hex_to_float(h):
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

def set_label(ax):#设置坐标系名称和长度
	

	ax.set_zlabel('Z')
	ax.set_ylabel('Y')
	ax.set_xlabel('X')
   
	ax.set_xlim3d(0,100)

	ax.set_ylim3d(-100,100)

	ax.set_zlim3d(0,20)

def point_to_pcd(point):
	pcd = o3d.geometry.PointCloud()
	pcd.points = o3d.utility.Vector3dVector(point)
	return pcd
def pcd_to_point(pcd):
	point=np.asarray(pcd.points)
	return point 

def Xyz_compute(result,point):
	method_id=binascii.b2a_hex(result[2:4])#帧里面的方式ID
	#print(f'该帧的方法id为{method_id}')
	if method_id==b'0150':
		#point=np.empty(shape=[0,3],dtype=float)#不做多帧融合时使用
		n=0
		HexNumPoint=binascii.b2a_hex(result[-27:-23])
		HexAzAngleCor=binascii.b2a_hex(result[-23:-19])
		HexElAngleCor=binascii.b2a_hex(result[-19:-15])
		NumPoint=int(HexNumPoint,16)
		AzAngleCor=hex_to_float(HexAzAngleCor)
		ElAngCor=hex_to_float(HexElAngleCor)

		for num in range(0,NumPoint):                       
				HexInValidFlag=format(result[109+(44*num)],'x').zfill(2)	
				HexAzAngle=binascii.b2a_hex(result[101+(44*num):105+(44*num)])
				HexELAngle=binascii.b2a_hex(result[110+(44*num):114+(44*num)])
				HexRaDist=binascii.b2a_hex(result[118+(44*num):122+(44*num)])
				HexRaVl=binascii.b2a_hex(result[126+(44*num):130+(44*num)])
				HexRCS=format(result[134+(44*num)],'x').zfill(2)
				HexPR=format(result[137+(44*num)],'x').zfill(2)
				RCS= hex_to_sint(HexRCS)
				PR=int(HexPR,16)	
				RaVl=hex_to_float(HexRaVl)

				if HexInValidFlag=='00' and (HexAzAngle!='00000000' or HexELAngle!='00000000' or HexRaDist!='00000000') and RCS in range(2,128)and PR>90 and np.fabs(RaVl)>0.003:
					n+=1 
					Az_angle=hex_to_float(HexAzAngle)+AzAngleCor
					El_angle=hex_to_float(HexELAngle)+ElAngCor
					RaDist=hex_to_float(HexRaDist)
					X_pos=RaDist*np.cos(El_angle)*np.cos(Az_angle)
					Y_pos=RaDist*np.cos(El_angle)*np.sin(Az_angle)
					Z_pos=RaDist*np.sin(El_angle)
					# X_vl=RaVl*cp.cos(El_angle)*cp.cos(Az_angle)
					# Y_vl=RaVl*cp.cos(El_angle)*cp.sin(Az_angle)
					# Z_vl=RaVl*cp.sin(El_angle)

					Xyz=np.asarray([X_pos,Y_pos,Z_pos])

					point=np.vstack([point,Xyz])
					#print(f'第{num}个点的坐标为：{Xyz},RCS值为{RCS},径向速度为：{RaVl}存在概率为{PR}')

				else:
								   
					continue
	return point
def Count_points(result):
	HexNumPoint = binascii.b2a_hex(result[-27:-23])
	NumPoint = int(HexNumPoint, 16)
	return NumPoint

def point_process(point):
	pcd = tools.point_to_pcd(point)
	pcd = filters.pass_through(pcd, limit_min=0, limit_max=25, filter_value_name="z")
	pcd = filters.pass_through(pcd, limit_min=0, limit_max=300, filter_value_name="x")

	cl, ind = pcd.remove_statistical_outlier(nb_neighbors=15, std_ratio=0.5)

	pcd = pcd.select_by_index(ind)
	# hull=filters.hull_pcd(pcd,ax)
	# obb=filters.create_obb(pcd,ax)
	point = tools.pcd_to_point(pcd)
	return point