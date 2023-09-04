from string import printable
from 报文重组 import *
import base64
from tool import *
import math
import numpy as np
import open3d as o3d
import time
def read_show(pcap_path,txt_path):
    f1=open(pcap_path,"rb")
    f2=open(txt_path,"a")
    pcap = dpkt.pcap.Reader(f1)
    num=0
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    pointcloud = o3d.geometry.PointCloud()
    vis.add_geometry(pointcloud)
    np.set_printoptions(suppress= True)
    for timestamp, buf in pcap:
        eth= dpkt.ethernet.Ethernet(buf)
        ip=eth.data
        print(f'在第{num}帧内')
        f2.write(f'在第{num}帧内 \n')
        udp=ip   
        num+=1
        point=np.empty(shape=[0,3],dtype=float)
        for i in range(0,800):
            HexAzAngle=format(udp[95+(44*i)],'x').zfill(2)+format(udp[96+(44*i)],'x').zfill(2)+format(udp[97+(44*i)],'x').zfill(2)+format(udp[98+(44*i)],'x').zfill(2)
            HexELAngle=format(udp[104+(44*i)],'x').zfill(2)+format(udp[105+(44*i)],'x').zfill(2)+format(udp[106+(44*i)],'x').zfill(2)+format(udp[107+(44*i)],'x').zfill(2)
            HexRaDist=format(udp[112+(44*i)],'x').zfill(2)+format(udp[113+(44*i)],'x').zfill(2)+format(udp[114+(44*i)],'x').zfill(2)+format(udp[115+(44*i)],'x').zfill(2)
            HexRCS==format(udp[128+(44*i)],'x').zfill(2)
            RCS=hex_to_float(HexRCS)
            #在将分片全部合并好的集群帧数据中，方位角（AzimuthAngle）、俯仰角（ElevationAngle）和径向距离（RadialDistance）均按照IEEE754标准以八位十六进制数的形式存放为单精度浮点数，
            #其在数据帧中的起始位置分别为95、104、112。为了防止转换后形如“0a”的数字前一位的0被省略，需要用zfill函数填充。
            if (HexAzAngle!='00000000')and(HexELAngle!='00000000')and(HexRaDist!='00000000')and RCS>-1:
            
               
           
                Az_angle=hex_to_float(HexAzAngle)
                El_angle=hex_to_float(HexELAngle)
                RaDist=hex_to_float(HexRaDist)
                X_pos=RaDist*math.cos(El_angle)*math.cos(Az_angle)
                Y_pos=RaDist*math.cos(El_angle)*math.sin(Az_angle)
                Z_pos=RaDist*math.sin(El_angle)
                point=np.append(point,[[X_pos,Y_pos,Z_pos]],axis=0)
                
                print(f'第{i}个目标点的坐标为：{X_pos},{Y_pos},{Z_pos}')
        np.savetxt(f2,point)
     
       
        pointcloud.points = o3d.utility.Vector3dVector(point)  # 如果使用numpy数组可省略上两行    
        vis.update_geometry(pointcloud)#刷新窗口内点云的状态
        vis.reset_view_point(True)#视角锁定在原点
        vis.poll_events()
        vis.update_renderer()
        #time.sleep(0.2)

            
         
  




