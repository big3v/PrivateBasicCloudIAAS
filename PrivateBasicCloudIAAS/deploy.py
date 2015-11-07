'''
Created on Oct 31, 2015

@author: yassine

IN PROGRESS 3
'''
import os
import subprocess
import platform
import sys
import commands
import psutil
import getpass
import time

def CSConfig1(xencpunum, xenmem):
    print("Configuring CloudStack ...")
    print('start downloading vxs01.qcow2 ...')
    subprocess.check_output(['wget https://big3v.com/CSIAAS/vxs01.qcow2 -P /var/lib/libvirt/images'], shell=True)
    print('vxs01.qcow2 downloaded')
    subprocess.check_output(["wget https://big3v.com/CSIAAS/vxs01.xml -P ./resources"], shell=True)
    print('vxs01.xml downloaded')
    print('start downloading vMgmtS01.qcow2 ...')
    subprocess.check_output(['wget https://big3v.com/CSIAAS/vMgmtS01.qcow2 -P /var/lib/libvirt/images'], shell=True)
    print('vMgmtS01.qcow2 downloaded')
    subprocess.check_output(["wget https://big3v.com/CSIAAS/vmgmts01.xml -P ./resources"], shell=True)
    print('vmgmts01.xml downloaded')    
    subprocess.check_output(["wget https://big3v.com/CSIAAS/systemvm64template-4.5-xen.vhd.bz2 -P ./resources"], shell=True)
    newxenmem = int(float(xenmem) / 1000 - 4096000)
    subprocess.check_output(['sed -i "/vcpu/s/>[^<]*</>' + str(xencpunum) + '</" ./resources/vxs01.xml'], shell=True)
    subprocess.check_output(['sed -i "/currentMemory/s/>[^<]*</>' + str(newxenmem) + '</" ./resources/vxs01.xml'], shell=True)
    subprocess.check_output(['sed -i "/memory/s/>[^<]*</>' + str(newxenmem) + '</" ./resources/vxs01.xml'], shell=True)  

def PreReboot():
    file = open("/etc/profile.d/CSConfig.sh", "w")
    file.write('#!/bin/sh\n')
    file.write('read -p "Press [Enter] key to continue CloudStack IAAS Setup ..."\n')
    file.write('workdir=' + str(os.path.dirname(os.path.abspath(__file__))) + '\n')
    file.write('cd $workdir\n')
    file.write('python CSConfig.py\n')
    file.write('rm /etc/profile.d/CSConfig.sh')
    file.close()

def SetNFS():
    print("Setting NFS Server ...")
    file = open("/etc/sysconfig/nfs", "a")
    file.write('\nLOCKD_TCPPORT=32803\n')
    file.write('LOCKD_UDPPORT=32769\n')
    file.write('MOUNTD_PORT=892\n')
    file.write('RQUOTAD_PORT=875\n')
    file.write('STATD_PORT=662\n')
    file.write('STATD_OUTGOING_PORT=2020')
    file.close()    
    subprocess.check_output(["""echo "\nRPCNFSDARGS='--no-nfs-version 4'" >> /etc/sysconfig/nfs"""], shell=True)
    subprocess.check_output(['systemctl enable nfs-server.service'], shell=True)
#    subprocess.check_output(['systemctl enable rpcbind.service'], shell=True)
#    subprocess.check_output(['service rpcbind start'], shell=True)
    subprocess.check_output(['service nfs start'], shell=True)
    subprocess.check_output(['mkdir -p /export/primary'], shell=True)
    subprocess.check_output(['mkdir -p /export/secondary'], shell=True)
    subprocess.check_output(["echo '/export  *(rw,async,no_root_squash,no_subtree_check)' > /etc/exports"], shell=True)
    subprocess.check_output(['exportfs -a'], shell=True)
    subprocess.check_output(['chkconfig nfs-server on'], shell=True)
    subprocess.check_output(['chkconfig rpcbind on'], shell=True)
    print('NFS Server Done!') 

def GetPassword(prompt):
    pw1 = getpass.getpass(prompt)
    print "Confirm ",
    pw2 = getpass.getpass(prompt)
    
    if pw1 == pw2:
        return str(pw1)
    else:
        print 'BAD: you provided different entries.'
        return GetPassword(prompt)

def CheckHost():
    checkresult = ''
    checkbool = True
    distname = platform.dist()[0]
    distversion = platform.dist()[1]
    distversion = distversion[0:1]
    if not (distname == "centos" and distversion == "7"):
        checkresult = "OS Check: NOK (Please use Centos 7)"
        checkbool = False
    else:
        checkresult = "OS Check: OK"
        
    cpunum = commands.getoutput("grep -c processor /proc/cpuinfo")
    if cpunum < 4:
        checkresult = checkresult + "\n" + "CPU Check: NOK (Please make sure you have 4 CPUs or more.)"
        checkbool = False
    else:
        checkresult = checkresult + "\n" + "CPU Check: OK"
        
    memsize = psutil.virtual_memory().total
    if memsize < 8000000000:
        checkresult = checkresult + "\n" + "Memory Check: NOK (You need 8 Go or more)"
        checkbool = False
    else:
        checkresult = checkresult + "\n" + "Memory Check:  OK"
            
    disksize = psutil.disk_usage('/').total
    if disksize < 200000000000:
        checkresult = checkresult + "\n" + "Disk Check: NOK (You need 200 Go or more)"
        checkbool = False
    else:
        checkresult = checkresult + "\n" + "Disk Check:  OK"
    
    vtsupport = len(subprocess.check_output(['cat /proc/cpuinfo| egrep "vmx|svm"'], shell=True))
    if vtsupport == 0:
        checkresult = checkresult + "\n" + "Virtualization Support Check: NOK (Your system does not support virtualization)"
        checkbool = False
    else:
        checkresult = checkresult + "\n" + "Virtualization Support Check: OK"    
    
    print(checkresult)
    return [ checkbool, cpunum, memsize]

def HostConfig():
    print("Configuring Centos Host ...")
    print('Updating host ...')
    subprocess.check_output(['yum -y update'], shell=True)
    print('Update complete.')
    print('Installing Virtualization Tools ...')
    subprocess.check_output(['yum -y groupinstall "Virtualization Tools" --setopt=group_package_types=mandatory,default,optional'], shell=True)
    subprocess.check_output(['yum -y install nano qemu-kvm libvirt virt-manager virt-install libvirt-python python-virtinst virt-top libguestfs-tools bridge-utils nfs-utils nfs-utils-lib'], shell=True)
    subprocess.check_output(["""sed -i 's/GRUB_CMDLINE_LINUX="/GRUB_CMDLINE_LINUX="kvm-intel.nested=1 /g' /etc/default/grub"""], shell=True)
    subprocess.check_output(['grub2-mkconfig -o /boot/grub2/grub.cfg'], shell=True)
    print('Virtualization Tools Installed.')
    
def InstallVPN():
    print('Installing VPN Server ...')
    subprocess.check_output(["wget https://big3v.com/CSIAAS/softether-vpnserver-v4.18-9570-rtm-2015.07.26-linux-x64-64bit.tar.gz -P ./resources"], shell=True)
    subprocess.check_output(['tar xzvf  ./resources/softether-vpnserver-v4.18-9570-rtm-2015.07.26-linux-x64-64bit.tar.gz'], shell=True)
    print('Installing VPN Server (getting stuff) ...')
    subprocess.check_output(['yum -y groupinstall "Development Tools" --setopt=group_package_types=mandatory,default,optional'], shell=True)
    print('Installing VPN Server (making vpnserver) ...')
    subprocess.check_output(['printf "1\n1\n1\n" | make -C ./vpnserver'], shell=True)    
    subprocess.check_output(['mv ./vpnserver /usr/local'], shell=True)
    print('Installing VPN Server (configuring vpnserver) ...')
    subprocess.check_output(['chmod 600 /usr/local/vpnserver/*'], shell=True)
    subprocess.check_output(['chmod 700 /usr/local/vpnserver/vpnserver'], shell=True)
    subprocess.check_output(['chmod 700 /usr/local/vpnserver/vpncmd'], shell=True)
    subprocess.check_output(['cp ./resources/vpnserver /etc/init.d'], shell=True)
    subprocess.check_output(['chmod 755 /etc/init.d/vpnserver'], shell=True)
    subprocess.check_output(['/etc/init.d/vpnserver start'], shell=True)
    time.sleep(10)
    try:
        subprocess.check_output(['mkdir /var/lock/subsys'], shell=True)
    except:
        pass
    subprocess.check_output(['chkconfig --add vpnserver'], shell=True)
    subprocess.check_output(['/etc/init.d/vpnserver stop'], shell=True)
    subprocess.check_output(['rm -rvf /usr/local/vpnserver/backup.vpn_server.config*'], shell=True)
    subprocess.check_output(["sed -i 's/bool Disabled false/bool Disabled true/g' /usr/local/vpnserver/vpn_server.config"], shell=True)
    subprocess.check_output(['service vpnserver restart'], shell=True)
    vpnserverpwd = GetPassword("Enter VPN Server Password:")
    vpnuserpwd = GetPassword("Enter VPN User Password:")    
    vpnpsk = GetPassword("Enter VPN Preshared Key:")    
    subprocess.check_output(['/usr/local/vpnserver/vpncmd /server localhost /adminhub:DEFAULT /cmd ServerPasswordSet ' + vpnserverpwd], shell=True)
    subprocess.check_output(['/usr/local/vpnserver/vpncmd /server localhost /password:' + vpnserverpwd + ' /adminhub:DEFAULT /cmd SecureNatEnable'], shell=True)
    subprocess.check_output(['/usr/local/vpnserver/vpncmd /server localhost /password:' + vpnserverpwd + ' /adminhub:DEFAULT /cmd UserCreate vpnuser01 /GROUP:none /REALNAME:none /NOTE:none'], shell=True)
    subprocess.check_output(['/usr/local/vpnserver/vpncmd /server localhost /password:' + vpnserverpwd + ' /adminhub:DEFAULT /cmd UserPasswordSet vpnuser01 /PASSWORD:' + vpnuserpwd], shell=True)
    subprocess.check_output(['/usr/local/vpnserver/vpncmd /server localhost /password:' + vpnserverpwd + ' /adminhub:DEFAULT /cmd IPsecEnable /L2TP:yes /L2TPRAW:yes /ETHERIP:yes /PSK:' + vpnpsk + ' /DEFAULTHUB:DEFAULT'], shell=True)
    subprocess.check_output(['/usr/local/vpnserver/vpncmd /server localhost /password:' + vpnserverpwd + ' /cmd BridgeCreate DEFAULT /DEVICE:virbr0'], shell=True)
    subprocess.check_output(['/usr/local/vpnserver/vpncmd /server localhost /password:' + vpnserverpwd + ' /adminhub:DEFAULT /cmd SecureNatHostSet /MAC:none /IP:192.168.30.1 /MASK:255.255.255.0'], shell=True)
    subprocess.check_output(['/usr/local/vpnserver/vpncmd /server localhost /password:' + vpnserverpwd + ' /adminhub:DEFAULT /cmd DhcpSet /START:192.168.30.10 /END:192.168.30.200 /MASK:255.255.255.0 /EXPIRE:7200 /GW:none /DNS:192.168.30.1 /DNS2:none /DOMAIN:none /LOG:yes'], shell=True)
    print('VPN Server Installed.')

print("Checking prerequisites ...")
resCheckHost = CheckHost() 
if resCheckHost[0]:
    print("Prerequisites OK")
else:
    print("Sorry, prerequisites NOK :(")
    sys.exit(1)

HostConfig()
InstallVPN()
SetNFS()
CSConfig1(resCheckHost[1], resCheckHost[2])
PreReboot()
raw_input("CloudStack IAAS configuration will continue after reboot. Press [Enter] to continue...")
subprocess.check_output(['reboot'], shell=True)