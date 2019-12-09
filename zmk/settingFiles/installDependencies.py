import subprocess
import sys
import os

packages = [
    'django',
    'django-rest-framework',
    'django-rest-swagger',
    'tpot',
    'opencv-python',
    'django-cors-headers',
    'tensorflow==1.9.0',
    'keras',
    'imutils',
    'lxml'
]
def installPackage(package):
    subprocess.call([sys.executable, "-m", "pip", "install", "--user", package])

def install():
    print(':::: Installing dependencies for environment : ',os.environ['CONDA_DEFAULT_ENV'],' ::::\n')
    for pck in packages:
        print('\n',pck.capitalize(),'-->\n')
        installPackage(pck)