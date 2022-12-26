# formal-methods-cf-systems
Formal Methods for Cyber-Physical Systems assignments ; Master's Degree in Computer Science @ UniPd

## Using the compose environment
- provided you have a working installation of docker, you can easily devlop inside an ad-hoc container with a prepared environment
- simply run: `docker compose up --build` to start the env. The first time this will pull the required stuff and build the image. Then a container will be started with the current folder binded in `/code` inside the container
  - leave the window with the compose running open, closing it will stop the container
  - to turn down the environment, simply `CTRL+C` in the compose window
- open a new terminal window and connect to the container `docker exec -ti formal-methods-cf-systems-python-1 bash`
  - now you have a shell with the all the repo mounted in which you can freely operate. This will work as long as the compose is running
  - to quit the shell just type `CTRL+D`