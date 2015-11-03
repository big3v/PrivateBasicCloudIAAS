'''
Created on Nov 2, 2015

@author: yassine
In Progress 1
'''
import subprocess
import time
import paramiko
import atexit

class myssh:

    def __init__(self, host, user, password, port = 22):
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host, port=port, username=user, password=password)
        atexit.register(client.close)
        self.client = client

    def __call__(self, command):
        stdin,stdout,stderr = self.client.exec_command(command)
        sshdata = stdout.readlines()
        for line in sshdata:
            print(line)
        return sshdata 

def CSConfig2_rem():
    print("Configuring CloudStack ...")
    subprocess.check_output(['virsh define ./resources/vxs01.xml'], shell=True)
    print('vxs01 vm created ...')
    subprocess.check_output(['virsh define ./resources/vmgmts01.xml'], shell=True)
    print('vMgmtS01 vm created ...')
    subprocess.check_output(['virsh start vMgmtS01'], shell=True)
    time.sleep(30)
    mgmtip = '192.168.122.10'
    mgmtuser = 'root'
    mgmtpwd = 'Fa26Lio5'
    remote = myssh(mgmtip,mgmtuser,mgmtpwd)
    print('Mounting NFS Secondary')
    remote("mount -t nfs 192.168.122.1:/export/secondary /mnt/secondary")
    print('cloudstack-setup-databases Start')
    remote("cloudstack-setup-databases cloud:Fa26Lio5@localhost --deploy-as=root:Fa26Lio5 -i 192.168.122.10")
    print('cloudstack-setup-databases Done')
    remote("cloudstack-setup-management")
    print('Install Template Start')
    remote("/usr/share/cloudstack-common/scripts/storage/secondary/cloud-install-sys-tmplt -m /mnt/secondary -u https://big3v.com/CSIAAS/systemvm64template-4.5-xen.vhd.bz2 -h xenserver -F")
    print('Install Template Done')
    remote("service cloudstack-management start")
    remote("chkconfig cloudstack-management on")
    subprocess.check_output(['virsh start vXS01'], shell=True)

def CSConfig2():
    print("Configuring CloudStack ...")
    subprocess.check_output(['service vpnserver stop'], shell=True)
    subprocess.check_output(['virsh define ./resources/vxs01.xml'], shell=True)
    print('vxs01 vm created ...')
    subprocess.check_output(['virsh define ./resources/vmgmts01.xml'], shell=True)
    print('vMgmtS01 vm created ...')
    subprocess.check_output(['virsh start vMgmtS01'], shell=True)
    subprocess.check_output(["wget https://big3v.com/CSIAAS/sshpass-1.05.tar -P ./resources"], shell=True)
    subprocess.check_output(['tar xvf ./resources/sshpass-1.05.tar'], shell=True)
    subprocess.check_output(['./sshpass-1.05/configure'], shell=True)
    subprocess.check_output(['make install install_root=./sshpass-1.05'], shell=True)
    time.sleep(30)
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
    subprocess.check_output(['virsh start vXS01'], shell=True)
    print('Waiting for CloudStack Manager to initialize (5 min) ...')
    time.sleep(300)
    subprocess.check_output(['service vpnserver start'], shell=True)
    
CSConfig2()
print('Congratulation, your CloudStack IAAS is ready!')