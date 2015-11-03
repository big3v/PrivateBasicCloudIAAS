'''
Created on Nov 2, 2015

@author: yassine
In Progress 1
'''
import subprocess

def CSConfig2():
    print("Configuring CloudStack ...")
    subprocess.check_output(['virsh define ./resources/vxs01.xml'], shell=True)
    print('vxs01 vm created ...')
    subprocess.check_output(['virsh define ./resources/vmgmts01.xml'], shell=True)
    print('vMgmtS01 vm created ...')
    subprocess.check_output(['virsh start vXS01'], shell=True)
    subprocess.check_output(['virsh start vMgmtS01'], shell=True)
    subprocess.check_output(["wget https://big3v.com/CSIAAS/sshpass-1.05.tar -P ./resources"], shell=True)
    subprocess.check_output(['tar xvf ./resources/sshpass-1.05.tar'], shell=True)
    subprocess.check_output(['./sshpass-1.05/configure'], shell=True)
    subprocess.check_output(['make install install_root=./sshpass-1.05'], shell=True)
    subprocess.check_output(['sshpass -p "Fa26Lio5" ssh -o StrictHostKeyChecking=no root@192.168.122.10 "mount -t nfs 192.168.122.1:/export/secondary /mnt/secondary"'], shell=True)
    print('cloudstack-setup-databases Start')
    subprocess.check_output(['sshpass -p "Fa26Lio5" ssh -o StrictHostKeyChecking=no root@192.168.122.10 "cloudstack-setup-databases cloud:Fa26Lio5@localhost --deploy-as=root:Fa26Lio5 -i 192.168.122.10"'], shell=True)
    print('cloudstack-setup-databases Done')
    subprocess.check_output(['sshpass -p "Fa26Lio5" ssh -o StrictHostKeyChecking=no root@192.168.122.10 "cloudstack-setup-management"'], shell=True)
    print('Install Template Start')
    subprocess.check_output(['sshpass -p "Fa26Lio5" ssh -o StrictHostKeyChecking=no root@192.168.122.10 "/usr/share/cloudstack-common/scripts/storage/secondary/cloud-install-sys-tmplt -m /mnt/secondary -u http://big3v.com/img/vmgmts01/systemvm64template-4.5-xen.vhd.bz2 -h xenserver -F"  > /dev/null 2>&1 & '], shell=True)
    print('Install Template Done')
    subprocess.check_output(['sshpass -p "Fa26Lio5" ssh -o StrictHostKeyChecking=no root@192.168.122.10 "service cloudstack-management start"'], shell=True)
    subprocess.check_output(['sshpass -p "Fa26Lio5" ssh -o StrictHostKeyChecking=no root@192.168.122.10 "chkconfig cloudstack-management on"'], shell=True)
    
CSConfig2()
print('Congratulation, your CloudStack IAAS is ready!')