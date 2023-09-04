import dpkt
import math
from tool import *
import open3d as o3d
import cupy as np
import time
import matplotlib.pyplot as plt
def pack_combine(r_path,w_path):
    #newpacpfile = open(w_path, "wb")#可以写入组包好的pcap文件
    #writer = dpkt.pcap.Writer(newpacpfile)
    f = open(r_path, mode='rb') #python3
    f2=open(w_path,"a")
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

    first_flag = 1
    raw_data = []
    #vis = o3d.visualization.Visualizer() 
    #vis.create_window(width=3840, height=2160)
    #pointcloud = o3d.geometry.PointCloud()
    #render_option = vis.get_render_option()
    #render_option.background_color = np.array([255, 255, 255])  # 设置背景为黑色
    #render_option.point_size = 16.0  # 设置点云显示尺寸，尺寸越大，点显示效果越粗
    # 
    #render_option.show_coordinate_frame = True  # 显示坐标系
    #vis.add_geometry(pointcloud)#设置好创建的窗口
    np.set_printoptions(suppress= True)
    # 将时间戳和包数据分开，一层一层解析，其中ts是时间戳，buf存放对应的包
    fig = plt.figure()
    plt.ion()
    ax = fig.add_subplot(111, projection='3d')

    for (ts, buf) in pcap:
        
        try:
                eth = dpkt.ethernet.Ethernet(buf)  # 解包，物理层
                if not isinstance(eth.data, dpkt.ip.IP):  # 解包，网络层，判断网络层是否存在，
                    continue
                ip = eth.data
                

                if isinstance(ip.data, dpkt.udp.UDP):
                    udp=ip.data 
               #解包，判断传输层协议是否是UDP ; 分片的节点是ip.data.data 不然是 ip.data
                     
               
          

                if first_flag:
                    id=0
                    raw_data.append(udp.data)
                else:
                    
                    if (ip.offset == 0):
                        # 可以在这里对每次UDP分片的数量做更严格的限制，因为基本上同一个数据来源的分片数量是固定的，比如每次发送3000byte,除以MTU1500，那么每次都是分成2个片段
                        # 这里每个集群帧的数据被分成了25个片段，那么我就只要25个片段的数据，不是25个片段的数据就丢弃
                        
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
                    print(f"第{id}帧：")
                    f2.write(f'在第{id}帧内 \n')
                    method_id=format(result[2],'x').zfill(2)+format(result[3],'x').zfill(2)#帧里面的方式ID
                #print(f'该帧的方法id为{method_id}')
                    if method_id=='0150':
                        point=np.empty(shape=[0,3],dtype=float)
                        for num in range(0,800):                       
                                HexAzAngle=format(result[101+(44*num)],'x').zfill(2)+format(result[102+(44*num)],'x').zfill(2)+format(result[103+(44*num)],'x').zfill(2)+format(result[104+(44*num)],'x').zfill(2)
                                HexELAngle=format(result[110+(44*num)],'x').zfill(2)+format(result[111+(44*num)],'x').zfill(2)+format(result[112+(44*num)],'x').zfill(2)+format(result[113+(44*num)],'x').zfill(2)
                                HexRaDist=format(result[118+(44*num)],'x').zfill(2)+format(result[119+(44*num)],'x').zfill(2)+format(result[120+(44*num)],'x').zfill(2)+format(result[121+(44*num)],'x').zfill(2)
                                HexRCS=format(result[134+(44*num)],'x').zfill(2)
                                RCS=hex_to_sint(HexRCS)
                                if (HexAzAngle!='00000000' or HexELAngle!='00000000' or HexRaDist!='00000000')and RCS>1 :
                                    Az_angle=hex_to_float(HexAzAngle)
                                    El_angle=hex_to_float(HexELAngle)
                                    RaDist=hex_to_float(HexRaDist)
                                    X_pos=RaDist*math.cos(El_angle)*math.cos(Az_angle)
                                    Y_pos=RaDist*math.cos(El_angle)*math.sin(Az_angle)
                                    Z_pos=RaDist*math.sin(El_angle)
                                    point=np.append(point,[[X_pos,Y_pos,Z_pos]],axis=0)
                                  
                                    
                                    print(f'第{num}个点的坐标为：{X_pos},{Y_pos},{Z_pos},RCS值为{RCS}')
                                else: continue
                        
                       
                        np.savetxt(f2,point,fmt='%.16f')
                     
                        #pointcloud.points = o3d.utility.Vector3dVector(point)      
                        #vis.update_geometry(pointcloud)#刷新窗口内点云的状态
                        #vis.reset_view_point(True)#视角锁定在原点
                       
                        #vis.poll_events()
                        #vis.update_renderer()
                        #time.sleep(1)
                        #######可以使用open3d或matplotlib进行可视化操作
                        set_label(ax)
                        ax.scatter(point[:, 0].get(),point[:, 1].get(),point[:, 2].get())#使用cupy时应使用.get()方法转换类型
                        plt.pause(0.1)
                        ax.cla()
                        
                plt.show()       
        except Exception as err:
            print( "[error] %s" % err)
    f.close() 
    #newpacpfile.close()






