#!/bin/bash
if [ -z "$2"];
then
	export hostdir=$(pwd)
else
export hostdir=$2
fi
echo $hostdir
echo 2nd argument $2
set -a

sed -i "/^hostdir=/d" ~/.zmod/.env 
echo hostdir=$hostdir >> ~/.zmod/.env
source ~/.zmod/.env
echo after sourcing .sh file $hostdir
if [[ $1 = "up" || $1 = "" || $1 = "." ]];
then
echo Starting ZMOD
#cd $hostdir
cat ${COMPOSE_CONFIG} | envsubst | sudo docker-compose -f - up -d
docker exec -it nginx_zmod bash -c 'rm nginx/conf.d/default.conf; service nginx restart'
docker exec -it zmm bash -c 'echo "  inside zmm" && echo alias nyoka="/publish/nyokacli/client/bin/release/netcoreapp2.1/linux-x64/publish/nyoka" >> ~/.bashrc && echo "DONE"'
echo in $(pwd)

echo ZMOD is up now
else
        echo Stopping ZMOD
	sudo docker stop zmk1 zmk2 zmk3
        cat ${COMPOSE_CONFIG} | envsubst | sudo docker-compose -f - down
        echo ZMOD is stopped now
fi


