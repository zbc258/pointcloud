import imp
from tool import *
import math
import re
import time
import os
import sys
import numpy as np
import open3d as o3d
vis = o3d.visualization.Visualizer()
vis.create_window()
pointcloud = o3d.geometry.PointCloud()
vis.add_geometry(pointcloud)
def xyzpoints(data_list, write_path):
    data_str = "".join(data_list)
    #集群消息参考 
    service_id = "0000"
    method_id  = "0150" #通信协议显示，集群帧的method-ID为0336，转换为十六进制为0150
    length     = "00008a00"#十进制35328，为长度length；
    heard = service_id + method_id + length
    some_ip_heard = "0000"+"0000"+"01"+"01"+"02"+"00"
    str_refer = heard + some_ip_heard

    all_index = [r.span() for r in re.finditer(str_refer, data_str)]
    #索引形式[(3, 5), (9, 11), (13, 15), (15, 17)]
    if all_index == []:
        print("无集群帧")
    else:
        
        for tuple_index in all_index:
           
            #class point:
            #    def __init__(self):
            #        self.x=0
            #        self.y=0
            #        self.z=0
            #定义存放点云数据的类
            point=np.empty(shape=[0,3],dtype=float)
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
                        rcs         = shex2sint(data_str[rcs_idx : rcs_idx + 1 * 2])
                        x = math.cos(az_ang + az_ang_corr) * (math.cos(el_ang + el_ang_corr)*r)
                        y = math.sin(az_ang + az_ang_corr) * (math.cos(el_ang + el_ang_corr)*r)
                        z = math.sin(el_ang + el_ang_corr) * r


                        #point.x=x
                        #point.y=y
                        #point.z=z
                                                ##############此段为调用open3d进行显示
                        point=np.append(point,[[x,y,z]],axis=0)
                        print(f'第{i}个点的坐标为（{x},{y},{z}），速度为{v}，RCS值为{rcs}')
                pointcloud.points = o3d.utility.Vector3dVector(point)  # 如果使用numpy数组可省略上两行    
                vis.update_geometry(pointcloud)#刷新窗口内点云的状态
                vis.reset_view_point(True)#视角锁定在原点
                vis.poll_events()
                vis.update_renderer()
                        ######################此段为写入本地文件##########
                        #with open(write_path, "a") as f:
                        #    info = f"{point(i,0)} {point(i,1)} {point(i,2)} \n"
                        #    f.write(info)
                
                           
       
    return point


