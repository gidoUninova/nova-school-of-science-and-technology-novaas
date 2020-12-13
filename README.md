# NOVA Asset Administration Shell

Implementation of the Asset Administration Shell by NOVA School of Science and Technology


This repository contains file that are needed to build a docker image for NOVAAS.
In order to install and run it, dowload/clone the repository and build and run the dockerfile and/or the docker-compose file.

# Using dockerfile


# Using Docker-compose

The docker-compose commnad is the following :

`docker-compose up -d`

this 
docker build -t isee_results_fetcher .
Now that the image has been built, it still has to be launched, using that command :
docker run --env-file ./env.list isee_results_fetcher
Of course, there might be a need for adaptation of some parameters such as the database URL. If there are some adaptations needed, just open the env-file and modify the part that is needed.
