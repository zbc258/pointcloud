
import binascii
from filter import *
from scapy.all import *
from tool import *
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
def xyzpoints(data_list):
	
	data_str = "".join(data_list)
	#集群消息参考 
	service_id = "0000"
	method_id  = "0150" #通信协议显示，集群帧的method-ID为0336，转换为十六进制为0150
	length     = "00008a00"#十进制35328，为长度length；
	heard = service_id + method_id + length
	some_ip_heard = "0000"+"0000"+"01"+"01"+"02"+"00"
	str_refer = heard + some_ip_heard
	global point
	all_index = [r.span() for r in re.finditer(str_refer, data_str)]
	#索引形式[(3, 5), (9, 11), (13, 15), (15, 17)]
	if all_index == []:
		print("无集群帧")
	else:
		
		for tuple_index in all_index:
		   

			
			start_idx_detnList = tuple_index[1] + 20 * 2 #集群信息起始位置
			start_idx_detns    = start_idx_detnList + 65 * 2 #具体到每一个点
			start_num          = start_idx_detnList + 117 * 2 + 799 * 44 *2
			start_idx_az_ang_corr = start_idx_detnList + 121 * 2 + 799 * 44 *2
			start_idx_el_ang_corr  = start_idx_detnList + 125 * 2 + 799 * 44 *2

			number_points = int(data_str[start_num : start_num + 4 * 2],16)
		  
			az_ang_corr = hex_to_float(data_str[start_idx_az_ang_corr : start_idx_az_ang_corr + 4 * 2])
			el_ang_corr  = hex_to_float(data_str[start_idx_el_ang_corr  : start_idx_el_ang_corr + 4 * 2])


			if number_points != 0: #检查点云个数
				for i in range(0,number_points):
					start_idx = start_idx_detns + i * 44 * 2#集群帧中每个点信息占44字节
					flags_idx = start_idx + 8 * 2
					flags     = int(data_str[flags_idx:flags_idx + 1 * 2],16)
					if flags == 0: #标志位全0，表示该点有效
						az_ang_idx = start_idx #以方位角在数据包中的位置作为起始参考点
						el_ang_idx  = start_idx + 9 * 2#俯仰角在方位角后9个字节处
						r_idx     = start_idx + 17 * 2#半径在方位角后17字节处
						v_idx = start_idx+25*2#径向速度在方位角后25字节处
						rcs_idx       = start_idx + 33 * 2#RCS在方位角后33字节处
						az_ang = hex_to_float(data_str[az_ang_idx : az_ang_idx + 4 * 2])
						el_ang  = hex_to_float(data_str[el_ang_idx : el_ang_idx + 4 * 2])
						r           = hex_to_float(data_str[r_idx : r_idx + 4 * 2])
						v=hex_to_float(data_str[v_idx:v_idx+4*2])
						rcs         = hex_to_sint(data_str[rcs_idx : rcs_idx + 1 * 2])
						x = math.cos(az_ang + az_ang_corr) * (math.cos(el_ang + el_ang_corr)*r)
						y = math.sin(az_ang + az_ang_corr) * (math.cos(el_ang + el_ang_corr)*r)
						z = math.sin(el_ang + el_ang_corr) * r


						if rcs>5:
							point=np.vstack([point,[x,y,z]])
							print(f'第{i}个点的坐标为（{x},{y},{z}），速度为{v}，RCS值为{rcs}')
				
	   
	return point
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
			print(f'完成{num}帧集群接收')
			
			list_cluster[-1] = nn
			for i in list_cluster:
				if i == "":
					print("帧不完整")
			
			point=xyzpoints(list_cluster)
			#print(point)
			#if num%35==0:
			if point.shape[0] >= 2000:

				set_label(ax)
				pcd=point_to_pcd(point)
				pcd=pass_through(pcd,limit_min=0,limit_max=25,filter_value_name="z")
				cl,ind = pcd.remove_statistical_outlier(nb_neighbors=5,std_ratio=0.4)#再进行离群点滤除
				pcd=pcd.select_by_index(ind)
				hull_pcd(pcd,ax)
				aabb=create_obb(pcd,ax)
				point=pcd_to_point(pcd)
				ax.scatter3D(point[:,0],point[:,1],point[:,2],c='b',marker=".") 
				plt.pause(0.5)
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


	 
