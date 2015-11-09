'''
Created on Nov 1, 2015

@author: yassine
https://big3v.com

https://github.com/big3v/PrivateBasicCloudIAAS.git

NOT READY YET ...
'''
import subprocess

subprocess.call("yum -y update", shell=True)
subprocess.call("yum -y install python-devel gcc wget", shell=True)
subprocess.call("python ez_setup.py ", shell=True)
subprocess.call("easy_install pip", shell=True)
subprocess.call("pip install --upgrade pip", shell=True)
subprocess.call("pip install psutil", shell=True)
subprocess.call("pip install --upgrade psutil", shell=True)
subprocess.call("pip install paramiko", shell=True)
subprocess.call("chmod u+x deploy.py", shell=True)
subprocess.call("python deploy.py", shell=True)

