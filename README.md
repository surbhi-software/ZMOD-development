# Zementis Modeler (ZMOD)

[<img src="https://github.com/SoftwareAG/ZMOD/blob/master/docs/zmod_logo.png" alt="zmod_logo" height="80" style="float:right"/>](https://www.zmod.org/)

**Zementis modeler** is an open source machine learning and artificial intelligence platform for Data Scientist to solve business problems faster and quicker, build prototypes and convert them to actual project. The modeler helps from data preparation to model building and deployment, the tool supports a large variety of algorithms that can be run without a single line of code. The web based tool has various components which help Data Scientist of different skill levels to perfrom several model building tasks and provides deployment ready PMML files which can be hosted as a REST services.

Zementis Modeler allows it's user to cover a wide variety of algorithms and Deep Neural Network architectures, with minimal or No code enviornment. It is also one of the few deep-learning platforms to support the Predictive Model Markup Languaue (PMML) format, PMML allows for different statistical and data mining tools to speak the same language. The feature offerings of Zementis Modeler are:
* **Zementis AutoML** : Automatically train Machine learning models on data supports huge space of algorithms and hyper parameters tuning.
* **Zementis Model Editor** : Create Deep Neural Network models using drag and drop functionality, which supports wide variety of model layers, once model architecture is ready, train your model. Zementis Modeler Editor also comes with pre-trained architcture templates that helps in quick model building and training.
* **Jupyter Notebook** : Zementis Modeler comes with integrated Jupyter Notebook (For R and Python).
* **Tensorboard** : Zementis Modeler provides Tensorboard dashboard to show the progress of models.
* **Code Execution** : Zementis Modeler provides support of executing Python script files for more advance requirements.
* **REST API Support** : Zementis Modeler can be used using REST calls and can be used as a deployment tool.

**Zementis Modeler** comes to you with the complete source code in Python, .Net, Angular, docker files and extended HTML documentation on how to use guidelines, and a growing number of video, blogs and tutorials that help you familiarize yourself with the way Zementis Modeler supports a Data Scientist on becoming more productive.

# Installation
### Pre-requisites
Please pick your __installation instructions__ in the following according to the OS you are using.

**Keep 30 GB memory space for ZMOD application.**<br/>
**Docker 18.09 CE onwards**<br/>
**Docker-compose version 1.23.2**<br/>

__Note__ : 
* Installation time may take upto 20 mins depending on the machine type and/or internet connectivity.
* you can extract or pull images in pareller by opening multiple command prompts tab.

### Ubuntu 18.04+ Linux System/ Windows 10 machine/ Mac OS

 ## Linux Ubuntu System

  * If you do not have a standalone Linux system than it can be installed using your preferred virtualization software [VMWare](https://my.vmware.com/en/web/vmware/info/slug/desktop_end_user_computing/vmware_workstation_pro/15_0) or [Virtual Box](https://www.virtualbox.org/) or you install ZMOD directly on [Windows](#Windows) (preferred).

  * Install Ubuntu 18 on your virtual machine by
    * Downloading Ubuntu image [here](https://www.ubuntu.com/download/desktop)
    * An example of installing Ubuntu using VMWare [here](https://websiteforstudents.com/how-to-install-ubuntu-16-04-17-10-18-04-on-vmware-workstation-guest-machines/)

    * ZMOD application can be installed on your local system (read the first bullet point for system pre-requisite). In order to install ZMOD on local system, we need docker and docker-compose to be installed. Once you have required system ready, install docker CE by following instructions [here](https://docs.docker.com/install/linux/docker-ce/ubuntu/) and docker compose by following instructions [here](https://docs.docker.com/compose/install/). Note than docker-compose should be installed for the Linux version.


   __Note__ : Remember to do post installation steps for your respective OS for docker CE install. You can find the information in the same page for Docker CE installation.



### How to use this image 

#### If you have ZMOD tar images then use the below commands to load the images.

* Type the below command to load docker images.

  * docker load -i zementis-modeler-nginx.tar.tz
  * docker load -i zementis-modeler-zmm.tz
  * docker load -i zementis-modeler-zmk.tz

* Skip the first bullet point in next heading stating __how to download the images from docker hub__ and follow rest of the instructions.

__Note__ : Make sure that you download/copy the tar files to your local drive system.

#### Download the images from docker hub

* Pull the docker images in your system by typing the below commands:

    * docker pull store/softwareag/zementis-modeler-nginx:1.38.2
    * docker pull store/softwareag/zementis-modeler-zmm:1.38.2
    * docker pull store/softwareag/zementis-modeler-zmk:1.38.2

**Note** - Try prefix sudo with docker commands if you do not see any results or see an error.

  
  * Check if the docker images are loaded by typing the command:

    * docker image ls 

    [Sample Docker images snapshot from console]()

  * Remove older ZMOD docker images/container by typing:

    * docker rmi -f  ***image_name***
    * docker container rm -f ***container_name***

  * Once the images are loaded. Start ZMOD application by running the below command. Please make sure that docker-compose.yml and ZMOD.sh and startup.sh, lie in the same directory.
  
    * Run startup.sh to setup ZMOD command:

      * bash startup.sh
      * source ~/.bashrc

* You can start ZMOD application from any directory by typing any of the below command:
  
   * ZMOD up 
   * zmod up
   * zmod
   * ZMOD
   * ZMOD up /directory/
      * For example: ZMOD up /home/user/testing
   * zmod up /directory/
      * For example: ZMOD up /home/user/testing

* To stop the ZMOD application type the below command from the directory where ZMOD up was typed:

   * ZMOD down
   * zmod down

  
  * Type localhost on your browser(preferably incognito mode/private browsing) you should see the login page. Authenticate using your email/github and you should see **ZMOD** application in action now.
    
## Windows 10 machine

### How to use this image 

#### If you have ZMOD tar images then use the below commands to load the images.

* Type the below command to load docker images.

  * docker load -i zementis-modeler-nginx.tar.tz
  * docker load -i zementis-modeler-zmm.tz
  * docker load -i zementis-modeler-zmk.tz

* Skip the first bullet point in next heading stating __how to download the images from docker hub__ and follow rest of the instructions.

__Note__ : Make sure that you download/copy the tar files to your local drive system.


#### Download the images from docker hub

* Pull the docker images in your system by typing the below commands:

    * docker pull store/softwareag/zementis-modeler-nginx:1.38.2
    * docker pull store/softwareag/zementis-modeler-zmm:1.38.2
    * docker pull store/softwareag/zementis-modeler-zmk:1.38.2

### Run ZMOD in Windows Directly ###

  * ZMOD application can be installed on your local system (read the first bullet point for system pre-requisite). In order to install ZMOD on the local system, we need docker and docker-compose to be installed. Once you have required system ready, install docker CE by following instructions [here](https://docs.docker.com/docker-for-windows/install/) and docker compose by following instructions [here](https://docs.docker.com/compose/install/). Note than docker-compose should be installed for windows version.

   __Note__ : Remember to do post installation steps for your respective OS for docker CE install. You can find the information in the same page for Docker CE installation.

* Once the Docker Desktop for Windows is installed, start Windows Powershell as an administrator.
 
* Check if the docker images are loaded by typing the command:

    * docker image ls 

    [Sample Docker images snapshot from console]()

 * Remove older ZMOD docker images/container by typing:

    * docker rmi -f  ***image_name***
    * docker container rm -f ***container_name***

  * Once the images are loaded. Start ZMOD application by running the below command. Please make sure that docker-compose.yml and ZMOD_up.ps1 lie in the same directory.
   
* You can start ZMOD application from any directory by typing any of the below command:
  
   * ZMOD_up.ps1 

* Type localhost on your browser(preferably incognito mode/private browsing) you should see the login page. Authenticate using your email/GitHub and you should see **ZMOD** application in action now.

* To stop the ZMOD application type the below command from the directory where ZMOD_up.ps1 was typed:

   * ZMOD_down.ps1

### Run ZMOD in Windows through Linux ###
 * ZMOD can run on Windows 10 also by:
   * Installing Linux on your Windows 10 machine. See the section on how to install ZMOD in Linux Ubuntu for more details. Essentially through a virtualbox or VMWare, you can install Linux and run ZMOD on the host Windows 10 system.

* Install Cygwin compiler on Windows 10 to run bash scripts necessary to install and run ZMOD in Windows 10. Essentially here Linux environment is created inside Windows to emulate Linux behavior in order to run the application. More details on Cygwin Compiler can be found out [here](https://www.cygwin.com/)

* Once the Cygwin compiler is installed you can follow the steps to run ZMOD on a Linux machine. 

### Run ZMOD in Windows through Powershell scripting(In progress, to be updated) ###

## Mac OS machine

  * ZMOD application can be installed on your local system (read the first bullet point for system pre-requisite). In order to install ZMOD on the local system, we need docker and docker-compose to be installed. Once you have required system ready, install docker CE by following instructions [here](https://docs.docker.com/docker-for-mac/) and docker compose by following instructions [here](https://docs.docker.com/compose/install/). Note than docker-compose should be installed for the Mac version.

  __Note__ : Remember to do post installation steps for your respective OS for docker CE install. You can find the information in the same page for Docker CE installation.

### How to use this image 

#### If you have ZMOD tar images then use the below commands to load the images.

* Type the below command to load docker images.

  * docker load -i zementis-modeler-nginx.tar.tz
  * docker load -i zementis-modeler-zmm.tz
  * docker load -i zementis-modeler-zmk.tz

* Skip the first bullet point in next heading stating __how to download the images from docker hub__ and follow rest of the instructions.

__Note__ : Make sure that you download/copy the tar files to your local drive system.


#### Download the images from docker hub

* Pull the docker images in your system by typing the below commands:

    * docker pull store/softwareag/zementis-modeler-nginx:1.38.2
    * docker pull store/softwareag/zementis-modeler-zmm:1.38.2
    * docker pull store/softwareag/zementis-modeler-zmk:1.38.2

**Note** - Try prefix sudo with docker commands if you do not see any results or see an error.

  
  * Check if the docker images are loaded by typing the command:

    * docker image ls 

    [Sample Docker images snapshot from console]()

  * Remove older ZMOD docker images/container by typing:

    * docker rmi -f  ***image_name***
    * docker container rm -f ***container_name***


  * Once the images are loaded. Start ZMOD application by running the below command. Please make sure that docker-compose.yml and ZMOD.sh and startup.sh, lie in the same directory.
  
    * Run startup.sh to setup ZMOD command:

      * bash startup.sh
      * source ~/.bashrc


* You can start ZMOD application from any directory by typing any of the below command:
  
   * ZMOD up 
   * zmod up
   * zmod
   * ZMOD
   * ZMOD up /directory/
      * For example: ZMOD up /home/user/testing
   * zmod up /directory/
      * For example: ZMOD up /home/user/testing

* Type localhost on your browser(preferably incognito mode/private browsing) you should see the login page. Authenticate using your email/github and you should see **ZMOD** application in action now.

* To stop the ZMOD application type the below command from the directory where ZMOD up was typed:

   * ZMOD down
   * zmod down

# Getting familiar with Zementis Modeler :
Zementis Modeler has 5 sections : 
1. Data
2. Model
3. Code
4. Tasks
5. Assets

**Data** : In this section, user uploads the data and can manage the data by performing all the CRUD operations. The data section supports, zip folders, image files, mp4 files, csv files.

**Model** : In this section, all the models are being managed, all the models will be PMML format only. The model files can be of machine learning based models or Neural Network based models, the models can have only structure or can also have weights with the model structures.

**Code** : Code section supports Python script files (.py files) and Jupyter Notebook files (.ipynb files). A user can upload python script files, notebook files and execute them in the Zementis Modeler. There are no options of creating new files in the UI, a user has to upload his files and then only they will be ready for executions. A user can edit files once uploaded to the Zmenentis Modeler.

**Tasks** : This section provides information about all the running tasks in the Zementis Modeler System, it gives info about running or finished AutoML tasks, Deep Neural Network model training status, and if any code execution process status, and any jupyter notebook instance running, a user can delete a running task from this section.

**Assets** : Assets section provide more info regarding the available hardware systems, used ports and components of Zementis Modeler. if any process needs to be killed or resource to be freed can be controlled from this section.

# Quick Demo of Zementis Modeler :

[Demo 1 : Distracted Driver Use Case](https://www.zmod.org/learn/0SZHvRSJwyc)<br/>
[Demo 2 : AutoML](https://www.zmod.org/learn/6RUJ0Nk52u8)<br/>
[Demo 3 : Import data from Cumulocity](https://www.zmod.org/learn/_YCGPhMETF4)<br/>
[Demo 4 : Jupyter Notebook](https://www.zmod.org/learn/dm98Rjb8l6w)<br/>
[Demo 5 : Python Execution](https://www.zmod.org/learn/Hnu7lvcc0kc)<br/>


## Support

You can ask questions at:

*	[https://stackoverflow.com](https://stackoverflow.com) by tagging your questions with #pmml, #zmod
*	You can also post bug reports in [GitHub issues](https://github.com/SoftwareAG/ZMOD/issues) 
______________________
These tools are provided as-is and without warranty or support. They do not constitute part of the Software AG product suite. Users are free to use, fork and modify them, subject to the license agreement. While Software AG welcomes contributions, we cannot guarantee to include every contribution in the master project.	

Contact us at [TECHcommunity](mailto:technologycommunity@softwareag.com?subject=Github/SoftwareAG) if you have any questions.

 
