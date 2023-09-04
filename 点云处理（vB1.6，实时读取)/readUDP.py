
import binascii
import filter as filters
from scapy.all import *
import tools
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
import numpy as np
#show_interfaces()

#定义单帧 “片” 列表结构
list_cluster = [""] * 24
#定义标志位，确保当前正在处理集群帧的片
cluster_obj = -1
#定义帧id
id = -1
#定义回调函数
num=0
mplstyle.use('fast')
np.set_printoptions(suppress= True)
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')	
point=np.empty(shape=[0,3],dtype=float)

def packet_call(packet):
	#print(packet)
   #定义单帧 “片” 列表结构
	
	global list_cluster  
	#定义标志位，确保当前正在处理集群帧的片
	global cluster_obj  
	#定义帧id
	global id 
	#只采集集群的分片
	global num
	global point
	try:
		if packet.haslayer(IP):

			if packet['IP'].frag == 1:
				n = binascii.hexlify(packet[0]["Raw"].load)
				nn = str(n, encoding="utf-8")
				if nn[:32] == "0000015000008a000000000001010200":
				#以上各位分别代表：0000，serviceID；0150，十进制为336，methodID；00008a00，十进制35328，length；
				#000000000，sessionID和ClientID；0101，ProtocolVersion和InterfaceVersion；0200，messagetype和returncode。
					cluster_obj = 1      #表示该帧为集群帧
					id = packet['IP'].id #标识当前要组建的帧
					list_cluster[0] = nn


			elif packet['IP'].frag ==4256 and id == packet['IP'].id: #表示集群帧到了最后一片
				#由于通信协议规定了其集群帧的UDP报文内容长度为35346字节，而UDP报文传输的最大传输单元（MTU），即单次传输的数据量，为1500字节，
				#相除可得每段报文需要分为24片,而最后一片的偏移量为34048（位），即4256字节。
				n = binascii.hexlify(packet[0]["Raw"].load)
				nn = str(n, encoding="utf-8")
				cluster_obj = -1 #表示从当前片退出集群帧
				id = -1          #表示该帧已合并完
				num=num+1
				#print(f'完成{num}帧集群接收')

				list_cluster[-1] = nn
				for i in list_cluster:
					if i == "":
						print("帧不完整")

				point=tools.xyzpoints(list_cluster,point)
				#print(point)
				if num%30==0:
				#if point.shape[0] >= 3000:

					tools.set_label(ax)
					pcd = tools.point_to_pcd(point)
					pcd = filters.pass_through(pcd, limit_min=0, limit_max=25, filter_value_name="z")
					pcd = filters.pass_through(pcd, limit_min=0, limit_max=300, filter_value_name="x")

					cl, ind = pcd.remove_statistical_outlier(nb_neighbors=10, std_ratio=0.5)

					pcd = pcd.select_by_index(ind)
					# hull=filters.hull_pcd(pcd,ax)
					# obb=filters.create_obb(pcd,ax)
					point = tools.pcd_to_point(pcd)
					D = np.min(point[:, 0])
					pcd = tools.point_to_pcd(point)
					pcd = filters.pass_through(pcd, limit_min=D, limit_max=(D + 20), filter_value_name="x")
					point = tools.pcd_to_point(pcd)

					print(f"离岸边距离为{D}")
					ax.scatter3D(point[:, 0], point[:, 1], point[:, 2], c='b', marker=".")
					plt.pause(0.1)
					plt.cla()
					point=np.empty(shape=[0,3],dtype=float)



				list_cluster = [""] * 24#集群帧中报文内容长度为35346字节,被分为24片


			elif cluster_obj == 1 and id == packet['IP'].id: #说明在同一集群帧内
				n = binascii.hexlify(packet[0]["Raw"].load)
				nn = str(n, encoding="utf-8")
				idx = int((packet['IP'].frag - 1)/185)
				list_cluster[idx] = nn
	except Exception as err:
		print( "[error] %s" % err)
		exit()


	 
