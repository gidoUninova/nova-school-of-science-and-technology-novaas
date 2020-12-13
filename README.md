# NOVA Asset Administration Shell

Implementation of the Asset Administration Shell by NOVA School of Science and Technology


This repository contains file that are needed to build a docker image for NOVAAS.
In order to install and run it, dowload/clone the repository and build and run the dockerfile and/or the docker-compose file.

# Using dockerfile
The docker command to create the NOVAAS image is the following:

`docker build -t name_of_the_image:ver .`

Once the image has been created the followig docker command can be used to start a new container that runs the NOVAAS image:

`docker run -p 1880:1880 name_of_the_image:ver -d`

# Using Docker-compose

The docker-compose command is the following:

`docker-compose up -d`

To build and run the image. Furthermore, the command:

`docker-compose build`

can be used to build a new image.

# Run another version of NOVAAS from this base folder

NOVAAS has been designed in order to be as generic as possible, if you want to run your own version of the NOVAAS you should perform the following steps:
1. Add all the documentation files (datashees, user manuals, etc.) within the folder "file/aasx/docu";
2. Add an image of the concerned asset within the folder "files/images". Note that the name of the file **must** be kept -> novaas_concerned_asset.jpg;
3. Add the Manifest file within the folder "files/manifest". Note that the name of the file **must** be kept -> AmI_as_manifest.json. In particular this file follows the data model provided in and can be created by using the aasx-package-explorer tool (https://github.com/admin-shell-io/aasx-package-explorer) 

