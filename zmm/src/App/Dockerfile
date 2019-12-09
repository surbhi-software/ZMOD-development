FROM microsoft/dotnet:2.2-runtime AS base
WORKDIR /app

FROM microsoft/dotnet:2.2-sdk AS build
LABEL Name=jnb Version=0.0.1 


# Updating Ubuntu packages
RUN apt-get update && yes|apt-get upgrade
RUN apt-get install -y emacs

# Adding wget and bzip2
RUN apt-get install -y wget bzip2

# Add sudo
RUN apt-get -y install sudo

# Add user ubuntu with no password, add to sudo group
RUN adduser --disabled-password --gecos '' ubuntu
RUN adduser ubuntu sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
USER ubuntu
WORKDIR /home/ubuntu/
RUN chown -R ubuntu:ubuntu /home/ubuntu
RUN chmod 755 /home/ubuntu/
#RUN chmod a+rwx /home/ubuntu/
#RUN echo `pwd`

# Anaconda installing
RUN wget https://repo.continuum.io/archive/Anaconda3-5.0.1-Linux-x86_64.sh
RUN bash Anaconda3-5.0.1-Linux-x86_64.sh -b
RUN rm Anaconda3-5.0.1-Linux-x86_64.sh

# Set path to conda                       
#ENV PATH /root/anaconda3/bin:$PATH
ENV PATH /home/ubuntu/anaconda3/bin:$PATH

RUN whereis jupyter-notebook

# Updating Anaconda packages
RUN conda update conda
RUN conda update anaconda
RUN conda update --all

#install tensorflow
RUN conda install -c https://conda.anaconda.org/jjhelmus tensorflow
RUN whereis tensorboard
#tensorboard --logdir=run1:/tmp/tensorflow/ --port 6006

RUN mkdir -p zmm
RUN mkdir -p ZMOD

RUN chown -R ubuntu:ubuntu zmm
RUN chmod 755 zmm
RUN chmod 755 ZMOD

WORKDIR /app/zmm
RUN dotnet dev-certs https
RUN ls
ENTRYPOINT dotnet App.dll --environment=ProductionDocker  --urls https://+:5000