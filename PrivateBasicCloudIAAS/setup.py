'''
Created on Nov 1, 2015

@author: yassine

NOT READY YET ...
'''
import subprocess

subprocess.call("yum -y install python-devel python-pip gcc", shell=True)
subprocess.call("pip install --upgrade pip", shell=True)
subprocess.call("pip install psutil", shell=True)
subprocess.call("pip install --upgrade psutil", shell=True)
subprocess.call("chmod u+x deploy.py", shell=True)
subprocess.call("python deploy.py", shell=True)

