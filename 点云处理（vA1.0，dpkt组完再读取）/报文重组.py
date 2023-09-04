import dpkt
from tool import *
def pack_combine(r_path,w_path):
    newpacpfile = open(w_path, "wb")#写入组包好的pcap文件
    writer = dpkt.pcap.Writer(newpacpfile)
    f = open(r_path, mode='rb') #python3
    # 读取文件的magic字段，读完后还要把文件指针移到0位置
    magic_head = f.read(4)
    f.seek(0, 0)
    if magic_head == b'\n\r\r\n':
        pcap  = dpkt.pcapng.Reader(f)
    elif magic_head == b'\xd4\xc3\xb2\xa1':
        pcap  = dpkt.pcap.Reader(f)
    else:
        print("[DEBUG in PcapUtils] It is not a pcap or pcapng file")
    #判断读取的文件是pcap还是pcapng格式   

    first_flag = 1
    raw_data = []
    
    # 将时间戳和包数据分开，一层一层解析，其中ts是时间戳，buf存放对应的包
    for (ts, buf) in pcap:
        
        try:
                eth = dpkt.ethernet.Ethernet(buf)  # 解包，物理层
                if not isinstance(eth.data, dpkt.ip.IP):  # 解包，网络层，判断网络层是否存在，
                    continue
                ip = eth.data
                #print(ip.id, ip.offset)

                if isinstance(ip.data, dpkt.udp.UDP):
                    udp=ip.data 
               #解包，判断传输层协议是否是UDP ; 分片的节点是ip.data.data 不然是 ip.data
                     
               
          

                if first_flag:
                    
                    raw_data.append(udp.data)
                else:
                    
                    if (ip.offset == 0):
                        # 可以在这里对每次UDP分片的数量做更严格的限制，因为基本上同一个数据来源的分片数量是固定的，比如每次发送3000byte,那么每次都是分成2个片段
                        # 比如我这里每个数据被分成了9个片段，那么我就只要9个片段的数据，不是9个片段的数据就丢弃
                        if len(raw_data) != 25:
                             raw_data.clear()
                             raw_data.append(udp.data)
                             continue
                        result = b""
                        for i in raw_data:
                            result += i
                        tempeth.data  = result
                        writer.writepkt(tempeth, ts=ts)  # 如果不加ts参数的话，这个数据包的时间戳默认是当前时间！
                        newpacpfile.flush()
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
               
        except Exception as err:
            print( "[error] %s" % err)
    f.close() 
    newpacpfile.close()






