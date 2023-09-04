import dpkt
import tools
import filters
import numpy as np
import cupy as cp
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
import time
import socket


def pack_combine(r_path,w_path):
	#newpacpfile = open(w_path, "wb")#可以写入组包好的pcap文件
	#writer = dpkt.pcap.Writer(newpacpfile)
	f = open(r_path, mode='rb')
	f2=open(w_path,"a")
	pcap=tools.determine_type(f)

	first_flag = 1
	raw_data = []
	mplstyle.use('fast')
	np.set_printoptions(suppress= True)
	
	fig = plt.figure()
	
	ax = fig.add_subplot(111, projection='3d')
	point=np.empty(shape=(0,3),dtype=np.float64)
	plt.ion()
	
	result=b""
	#size=15#定义合并多少帧为一块
	sum_point=0
	for (ts, buf) in pcap:
		
		try:
				
				eth = dpkt.ethernet.Ethernet(buf)  # 解包，物理层
				if type(eth.data) == dpkt.ip.IP:
					ip = eth.data
					src = socket.inet_ntoa(ip.src)
					if src=="10.13.1.113":
						if type(ip.data) == dpkt.tcp.TCP:
							tcp = ip.data
						elif type(ip.data) == dpkt.udp.UDP:
							udp = ip.data
						elif type(ip.data) == dpkt.icmp.ICMP:
							icmp = ip.data
				#解包，判断传输层协议是否是UDP ; 分片的节点是ip.data.data 不然是 ip.data
						if first_flag:
							id=0
							raw_data.append(udp.data)
						else:

							if (ip.offset == 0):
								# 可以在这里对每次UDP分片的数量做更严格的限制，因为基本上同一个数据来源的分片数量是固定的，比如每次发送3000byte,除以MTU1500，那么每次都是分成2个片段
								# 这里每个集群帧的数据被分成了25个片段，那么只要25个片段的数据，不是25个片段的数据就丢弃

								if len(raw_data) != 25:
									raw_data.clear()
									result=b""
									raw_data.append(udp.data)
									continue

								result = b""
								for i in raw_data:
									result += i
								tempeth.data  = result
								#writer.writepkt(tempeth, ts=ts)  # 如果不加ts参数的话，这个数据包的时间戳默认是当前时间！
								#newpacpfile.flush()
								raw_data.clear()
								if not isinstance(udp.data, bytes):  # 可能存在其他类型数据
									continue
								raw_data.append(udp.data)
							else:
								# print(len(raw_data), "len(raw_data)", type(ip.data))
								if not isinstance(ip.data, bytes):  # 可能存在其他类型数据
									continue
								raw_data.append(ip.data)
								tempeth=udp
						first_flag = 0
						if result!=b'':#结果非空，说明合并完成
							id+=1
							#print(f"第{id}帧：")
							#f2.write(f'在第{id}帧内 \n')
							point=tools.Xyz_compute(result,point)
							sum_point=sum_point+tools.Count_points(result)
							#time.sleep(0.1)
							if point.shape[0]>=1000:

								#f2.write(f'在第{int(id/size)}块内 \n')
								np.savetxt(f2,point,fmt='%.16f')
								tools.set_label(ax)
								point=tools.point_process(point)
								D=np.min(point[:,0])
								pcd=tools.point_to_pcd(point)
								pcd=filters.pass_through(pcd,limit_min=D,limit_max=(D+20),filter_value_name="x")
								point=tools.pcd_to_point(pcd)

								print(f"离岸边距离为{D}")
								ax.scatter3D(point[:,0],point[:,1],point[:,2],c='b',marker=".")

								plt.pause(.05)
								ax.cla()
								point=np.empty(shape=(0,3),dtype=np.float64)

						plt.show()
		except Exception as err:
			print("[error] %s" % err)
	f.close() 







