docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker container prune -f
docker rmi $(docker images -q)
docker image prune -f
docker system prune -a