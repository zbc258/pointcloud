from asyncio.windows_events import NULL
import binascii
from xyz import *
from scapy.all import *
#show_interfaces()

#定义单帧 “片” 列表结构
list_cluster = [""] * 24
#定义标志位，确保当前正在处理集群帧的片
cluster_obj = -1
#定义帧id
id = -1
#定义回调函数
num=0
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
            
            xyzpoints(list_cluster,"./点云.txt")

            list_cluster = [""] * 24#集群帧中报文内容长度为35346字节,被分为24片


        elif cluster_obj == 1 and id == packet['IP'].id: #说明在同一集群帧内
            n = binascii.hexlify(packet[0]["Raw"].load)
            nn = str(n, encoding="utf-8")
            idx = int((packet['IP'].frag - 1)/185)
            list_cluster[idx] = nn
    except:
         exit()

