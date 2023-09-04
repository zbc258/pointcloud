#from 读取数据 import *
from 报文重组 import *

if __name__ == '__main__':
    w_path = "C:/Users/22521/Desktop/现场数据/8.pcapng"
    new_path="C:/Users/22521/Desktop/现场数据/new_8_1.pcap"
    pcd_path="C:/Users/22521/Desktop/现场数据/new_8.pcd"
    pack_combine(w_path,new_path)
    #read_show(new_path,pcd_path)
