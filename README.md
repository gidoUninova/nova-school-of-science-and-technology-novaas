# NOVA Asset Administration Shell

The NOVA Asset Administration Shell (NOVAAS) is an open source reference implementation and execution environment - developed by NOVA School of Science and Technology - for the Asset Administration Shell (AAS) concept proposed by the Reference Architectural Model for Industrie 4.0 (RAMI4.0). The AAS is an implementation of the concept of Digital Twin for industrial applications - in the context of the Industrie 4.0 - and establishes the cornerstone for interoperability between production assets.

This repository contains file that are needed to build a docker image for NOVAAS.
In order to install and run it, dowload/clone the repository and build and run the dockerfile and/or the docker-compose file.
The NOVAAS repository is preloaded with a set of files (documentation, asset, manifest) that are used to show the component. For creating a new specific NOVAAS these files need to be substituted with the proper ones.

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
1. Add all the documentation files (datashees, user manuals, etc.) within the folder "file/aasx/docu", the names of the files should be aligned with the names in the manifest;
2. Add an image of the concerned asset within the folder "files/images". Note that the name of the file **must** be kept -> novaas_concerned_asset.jpg;
3. Add the Manifest file within the folder "files/manifest". Note that the name of the file **must** be kept -> AmI_as_manifest.json. In particular this file follows the data model provided in https://www.plattform-i40.de/PI40/Redaktion/EN/Downloads/Publikation/Details_of_the_Asset_Administration_Shell_Part1_V3.html and can be created by using the aasx-package-explorer tool (https://github.com/admin-shell-io/aasx-package-explorer) ;
4. Change the httpauth file in the folder "files/httpauth" properly;
5. Run the docker and/0r docker-compose commands. 

