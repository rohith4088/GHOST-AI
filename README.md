
# GHOST-AI
PROJECT HELPER AI

### those who are contributing make sure you pull the repo and also build and compose the docker -image so that all the libraries are installed in docker and not system.

## docker and git  commands 
``git pull``
``docker-compose build``
``docker-compose up``

## for shutting down docker service
``docker-compose down``

# when a new requiremnt is added to a specific service only rebuild that service
``docker-compose up -d --force-recreate --no-deps --build <service_name>``


### There are two different docker files for both frontend and backend , so that they remain isloated
