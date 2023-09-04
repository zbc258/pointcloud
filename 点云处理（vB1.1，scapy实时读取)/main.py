from ast import Try
from pcd_create import *
import open3d as o3d
from scapy.all import *
from xyz import *
from readUDP import *



#try:
packet = sniff(offline="C:/Users/22521/Desktop/现场数据/8.pcapng",iface=None,count=0,prn = packet_call)

#packet= sniff(iface='Realtek PCIe GbE Family Controller',count=0,prn = packet_call,filter="host 10.13.1.113")



#creat_pcd('./点云.txt','./点云.pcd')#不转换也可以
#print('载入并渲染点云')

#except:
    #pcd = o3d.io.read_point_cloud('./点云.txt',format='xyz')
    #print(pcd)
    #print(np.asarray(pcd.points))
    #o3d.visualization.draw_geometries([pcd])