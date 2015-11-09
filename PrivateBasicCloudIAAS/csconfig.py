'''
Created on Nov 3, 2015

@author: yassine
https://big3v.com

'''
import subprocess
import time

def CSConfig2():
    print("Configuring CloudStack ...")
    subprocess.call(['service vpnserver stop'], shell=True)
    subprocess.call(['virsh define ./resources/vxs01.xml'], shell=True)
    print('vxs01 vm created ...')
    subprocess.call(['virsh define ./resources/vmgmts01.xml'], shell=True)
    print('vMgmtS01 vm created ...')
    subprocess.call(['service nfs restart'], shell=True)
    subprocess.call(['service rpcbind restart'], shell=True)
    subprocess.call(['virsh start vXS01'], shell=True)
    subprocess.call(['virsh start vMgmtS01'], shell=True)
    subprocess.call(['virsh autostart vMgmtS01'], shell=True)
    subprocess.call(['virsh autostart vXS01'], shell=True)
    subprocess.call(['service vpnserver start'], shell=True)
    subprocess.call(['rm -rvf PrivateBasicCloudIAAS'], shell=True)
    
CSConfig2()
print('Congratulation, your CloudStack IAAS is ready!')