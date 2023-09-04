
import os
import sys
import numpy as np

def creat_pcd(input_path, output_path):
    
    #Lodaing txt
    Full_Data = np.loadtxt(input_path)
    
    #Creating pcd
    if os.path.exists(output_path):
        os.remove(output_path)
    Output_Data = open(output_path, 'a')
    Output_Data.write('# .PCD v0.7 - Point Cloud Data file format\nVERSION 0.7\nFIELDS x y z rgba\nSIZE 4 4 4 4\nTYPE F F F U\nCOUNT 1 1 1 1')
    string = '\nWIDTH ' + str(Full_Data.shape[0])
    Output_Data.write(string)
    Output_Data.write('\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0')
    string = '\nPOINTS ' + str(Full_Data.shape[0])
    Output_Data.write(string)
    Output_Data.write('\nDATA ascii')
    for j in range(Full_Data.shape[0]):
        #R=Full_Data[j,3]
        #G=Full_Data[j,4]
        #B=Full_Data[j,5]
        #value = (int(R) << 16 | int(G) << 8 | int(B))
        string = ('\n' + str(Full_Data[j,0]) + ' ' + str(Full_Data[j, 1]) + ' ' +str(Full_Data[j, 2]) )
        Output_Data.write(string)
    Output_Data.close()



