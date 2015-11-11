'''
Created on Oct 31, 2015

@author: yassine
https://big3v.com

'''
import os
import subprocess
import platform
import sys
import commands
import psutil
import getpass
import time
stuffurl = 'https://big3v.com/CSIAAS_1.0.0/'

def CSConfig1(xencpunum, xenmem):
    print('Start downloading disk images (~3G, please be patient) ...')
    subprocess.call(['wget ' + stuffurl + 'qcows.tar.gz -P ./resources'], shell=True)
    subprocess.call(['tar xvzf ./resources/qcows.tar.gz -C /var/lib/libvirt/images --strip 2'], shell=True)
    print('Disk images downloaded')
    subprocess.call(['wget ' + stuffurl + 'vxs01.xml -P ./resources'], shell=True)
    print('vxs01.xml downloaded')
    subprocess.call(['wget ' + stuffurl + 'vmgmts01.xml -P ./resources'], shell=True)
    print('vmgmts01.xml downloaded')    
    newxenmem = int(float(xenmem) / 1000 - 4096000)
    subprocess.call(['sed -i "/vcpu/s/>[^<]*</>' + str(xencpunum) + '</" ./resources/vxs01.xml'], shell=True)
    subprocess.call(['sed -i "/currentMemory/s/>[^<]*</>' + str(newxenmem) + '</" ./resources/vxs01.xml'], shell=True)
    subprocess.call(['sed -i "/memory/s/>[^<]*</>' + str(newxenmem) + '</" ./resources/vxs01.xml'], shell=True)  

def PreReboot():
    file = open("/etc/profile.d/csconfig.sh", "w")
    file.write('#!/bin/sh\n')
    file.write('read -p "Press [Enter] key to continue CloudStack IAAS Setup ..."\n')
    file.write('workdir=' + str(os.path.dirname(os.path.abspath(__file__))) + '\n')
    file.write('cd $workdir\n')
    file.write('python csconfig.py\n')
    file.write('rm /etc/profile.d/csconfig.sh')
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
    subprocess.call(["""echo "\nRPCNFSDARGS='--no-nfs-version 4'" >> /etc/sysconfig/nfs"""], shell=True)
    subprocess.call(['wget ' + stuffurl + 'export.tar.gz -P ./resources'], shell=True)
    subprocess.call(['tar xvzf ./resources/export.tar.gz -C /'], shell=True)
    subprocess.call(["echo '/export  192.168.122.*(rw,async,no_root_squash,no_subtree_check)' > /etc/exports"], shell=True)
    subprocess.call(['exportfs -a'], shell=True)
    subprocess.call(['chkconfig nfs-server on'], shell=True)
    subprocess.call(['chkconfig rpcbind on'], shell=True)
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
    subprocess.call(['yum -y update'], shell=True)
    print('Update complete.')
    print('Installing Virtualization Tools ...')
    subprocess.call(['yum -y groupinstall "Virtualization Tools" --setopt=group_package_types=mandatory,default,optional'], shell=True)
    subprocess.call(['yum -y install nano qemu-kvm libvirt virt-manager virt-install libvirt-python python-virtinst virt-top libguestfs-tools bridge-utils nfs-utils nfs-utils-lib'], shell=True)
    subprocess.call(["""sed -i 's/GRUB_CMDLINE_LINUX="/GRUB_CMDLINE_LINUX="kvm-intel.nested=1 /g' /etc/default/grub"""], shell=True)
    subprocess.call(['grub2-mkconfig -o /boot/grub2/grub.cfg'], shell=True)
    print('Virtualization Tools Installed.')
    
def InstallVPN():
    print('Installing VPN Server ...')
    subprocess.call(['wget ' + stuffurl + 'softether-vpnserver-v4.18-9570-rtm-2015.07.26-linux-x64-64bit.tar.gz -P ./resources'], shell=True)
    subprocess.call(['tar xzvf  ./resources/softether-vpnserver-v4.18-9570-rtm-2015.07.26-linux-x64-64bit.tar.gz'], shell=True)
    print('Installing VPN Server (getting stuff) ...')
    subprocess.call(['yum -y groupinstall "Development Tools" --setopt=group_package_types=mandatory,default,optional'], shell=True)
    print('Installing VPN Server (making vpnserver) ...')
    subprocess.call(['printf "1\n1\n1\n" | make -C ./vpnserver'], shell=True)    
    subprocess.call(['mv ./vpnserver /usr/local'], shell=True)
    print('Installing VPN Server (configuring vpnserver) ...')
    subprocess.call(['chmod 600 /usr/local/vpnserver/*'], shell=True)
    subprocess.call(['chmod 700 /usr/local/vpnserver/vpnserver'], shell=True)
    subprocess.call(['chmod 700 /usr/local/vpnserver/vpncmd'], shell=True)
    subprocess.call(['cp ./resources/vpnserver /etc/init.d'], shell=True)
    subprocess.call(['chmod 755 /etc/init.d/vpnserver'], shell=True)
    subprocess.call(['/etc/init.d/vpnserver start'], shell=True)
    time.sleep(10)
    try:
        subprocess.call(['mkdir /var/lock/subsys'], shell=True)
    except:
        pass
    subprocess.call(['chkconfig --add vpnserver'], shell=True)
    subprocess.call(['/etc/init.d/vpnserver stop'], shell=True)
    subprocess.call(['rm -rvf /usr/local/vpnserver/backup.vpn_server.config*'], shell=True)
    subprocess.call(["sed -i 's/bool Disabled false/bool Disabled true/g' /usr/local/vpnserver/vpn_server.config"], shell=True)
    subprocess.call(['service vpnserver restart'], shell=True)
    subprocess.call(['/usr/local/vpnserver/vpncmd /server localhost /adminhub:DEFAULT /cmd ServerPasswordSet ' + vpnserverpwd], shell=True)
    subprocess.call(['/usr/local/vpnserver/vpncmd /server localhost /password:' + vpnserverpwd + ' /adminhub:DEFAULT /cmd SecureNatEnable'], shell=True)
    subprocess.call(['/usr/local/vpnserver/vpncmd /server localhost /password:' + vpnserverpwd + ' /adminhub:DEFAULT /cmd UserCreate vpnuser01 /GROUP:none /REALNAME:none /NOTE:none'], shell=True)
    subprocess.call(['/usr/local/vpnserver/vpncmd /server localhost /password:' + vpnserverpwd + ' /adminhub:DEFAULT /cmd UserPasswordSet vpnuser01 /PASSWORD:' + vpnuserpwd], shell=True)
    subprocess.call(['/usr/local/vpnserver/vpncmd /server localhost /password:' + vpnserverpwd + ' /adminhub:DEFAULT /cmd IPsecEnable /L2TP:yes /L2TPRAW:yes /ETHERIP:yes /PSK:' + vpnpsk + ' /DEFAULTHUB:DEFAULT'], shell=True)
    subprocess.call(['/usr/local/vpnserver/vpncmd /server localhost /password:' + vpnserverpwd + ' /cmd BridgeCreate DEFAULT /DEVICE:virbr0'], shell=True)
    subprocess.call(['/usr/local/vpnserver/vpncmd /server localhost /password:' + vpnserverpwd + ' /adminhub:DEFAULT /cmd SecureNatHostSet /MAC:none /IP:192.168.30.1 /MASK:255.255.255.0'], shell=True)
    subprocess.call(['/usr/local/vpnserver/vpncmd /server localhost /password:' + vpnserverpwd + ' /adminhub:DEFAULT /cmd DhcpSet /START:192.168.30.10 /END:192.168.30.200 /MASK:255.255.255.0 /EXPIRE:7200 /GW:none /DNS:8.8.8.8 /DNS2:8.8.4.4 /DOMAIN:none /LOG:yes'], shell=True)
    print('VPN Server Installed.')

vpnserverpwd = GetPassword("Set VPN Server Password:")
vpnuserpwd = GetPassword("Set VPN User Password:")    
vpnpsk = GetPassword("Set VPN Preshared Key:") 
print("Checking prerequisites ...")
resCheckHost = CheckHost() 
if resCheckHost[0]:
    print("Prerequisites OK")
else:
    print("Sorry, prerequisites NOK :(")
    sys.exit(1)

HostConfig()
SetNFS()
InstallVPN()
CSConfig1(resCheckHost[1], resCheckHost[2])
PreReboot()
raw_input("CloudStack IAAS configuration will continue after reboot. Press [Enter] to continue...")
subprocess.call(['reboot'], shell=True)