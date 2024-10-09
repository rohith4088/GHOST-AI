# GHOST-AI
PROJECT HELPER AI

### those who are contributing make sure you pull the repo and also build and compose the docker -image so that all the libraries are installed in docker and not system.

## docker and git  commands 
``git pull``

``docker run -it ubuntu``

### Execute the above command once to initiate a new container, After, initialize a container use the following command to note the name of the container to use the same container throughout the project.

`docker container ls -a`
### Note down the container name which is running with ubuntu image.

`docker run -it <container name>`
### Use your container name, so every time there is no need for new containers.

`docker-compose build`

`docker-compose up`


