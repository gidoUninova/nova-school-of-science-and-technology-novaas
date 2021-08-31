# NOVA Asset Administration Shell

The NOVA Asset Administration Shell (NOVAAS) is an open source reference implementation and execution environment - developed by NOVA School of Science and Technology - for the Asset Administration Shell (AAS) concept proposed by the Reference Architectural Model for Industrie 4.0 (RAMI4.0). 
The AAS implements the concept of the Digital Twin of a physical object turning it into an Industrie 4.0 component that facilitates interoperability in industrial applications.

This repository contains file that are needed to build a docker image for NOVAAS.
In order to install and run it, dowload/clone the repository and build and run the dockerfile and/or the docker-compose file.
The NOVAAS repository is preloaded with a set of files (documentation, asset, manifest) that are used to show the component. For creating a new specific NOVAAS these files need to be substituted with the proper ones.

## Using dockerfile
The docker command to create the NOVAAS image is the following:

`docker build -t name_of_the_image:ver .`

Once the image has been created the followig docker command can be used to start a new container that runs the NOVAAS image:

`docker run --env PORT_FORWARDING=1870 --env HOST=localhost --env BROKER_SERVICE_HOST=localhost --env BROKER_SERVICE_PORT=1883 -p 1870:1880 name_of_the_image:ver -d`

After executing the above commands, the NOVAAS will be accessible at the following link:

http://localhost:1870/ui 

![Semantic description of image](/source/images/Screenshot_2020-12-15_at_22.20.37.png)"NOVAAS Main Screen"

### Notes
The two environmental variables are needed to properly configure the internal iFrame node that is used to expose in the ui the dashboards for each one of the internal data sources. Specifically, the $HOST environmental variable should be the ip address of the host machine where NOVAAS is deployed. Setting this variable to localhost will only expose the dash tab within the ui in the host.

The NOVAAS embeds an MQTT client for pushing out data. This client needs to be configured. To do that it is possible to access the NOVAAS backend by using the following link:

http://localhost:1870

or by properly configure the following environmental variables: i) $BROKER_SERVICE_HOST that is used to set-up the host where the mqtt broker is running; and ii) $BROKER_SERVICE_PORT that is used to set-up the port used by the mqtt broker. 

![Semantic description of image](/source/images/Screenshot_2020-12-15_at_22.40.31.png)"NOVAAS Backend once user is logged in"

To access the backend the user needs to insert username and password. These are the default username and password from the node-red settings file, namely:

- username: admin
- password: password

## Using Docker-compose

The docker-compose command is the following:

`docker-compose up -d`

To build and run the image. Furthermore, the command:

`docker-compose build`

can be used to build a new image. The started docker container will run on port 1870,however it is possible to change this behaviour by setting the environmental variables PORT_FORWARDING and HOST in the .env file.

## Using the pre-built image

An already built image is part of the repository and can be accessed here:

https://gitlab.com/novaas/catalog/nova-school-of-science-and-technology/novaas/container_registry

## Run another version of NOVAAS from this base folder

NOVAAS has been designed in order to be as generic as possible, if you want to run your own version of the NOVAAS you should perform the following steps:
1. Add the environment model file within the folder "files/". Note that the name of the file **must** be kept -> model.aasx. In particular this file follows the data model provided in https://www.plattform-i40.de/PI40/Redaktion/EN/Downloads/Publikation/Details_of_the_Asset_Administration_Shell_Part1_V3.html and can be created by using the aasx-package-explorer tool (https://github.com/admin-shell-io/aasx-package-explorer); **The aasx-package-explorer tool allows to save the environment model in several formats. However, the file format currently supported by NOVAAS is "aasx w/ JSON"**;
1. Change the httpauth file in the folder "files/httpauth" properly;
1. Run the docker and/or docker-compose commands.

###Notes

The current aasx model file has been generated using the following version of the AASX Explorer selecting the option aasx w/ JSON:

https://github.com/admin-shell-io/aasx-package-explorer/releases/tag/v2020-11-16.alpha



## NOVAAS in action (Click on the Image to Show the Video)

[![Watch the video](/source/images/Screenshot_2020-12-15_at_22.20.37.png)](https://gitlab.com/gidouninova/novaas/-/blob/master/source/videos/NOVAAS_myMovie.mp4)

