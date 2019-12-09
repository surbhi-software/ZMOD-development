
docker-compose up -d
docker exec -it nginx_zmod bash -c 'rm nginx/conf.d/default.conf; service nginx restart'
docker exec -it zmm bash -c 'echo "  inside zmm" && echo alias nyoka="/publish/nyokacli/client/bin/release/netcoreapp2.1/linux-x64/publish/nyoka" >> ~/.bashrc && echo "DONE"'


