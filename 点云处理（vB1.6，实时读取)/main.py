from ast import Try
from scapy.all import *
from readUDP import *



packet = sniff(offline="C:/Users/22521/Desktop/现场数据/14.pcapng",iface=None,count=0,prn = packet_call)

#packet= sniff(iface='Realtek PCIe GbE Family Controller',count=0,prn = packet_call,filter="host 172.16.17.222")

plt.show()
