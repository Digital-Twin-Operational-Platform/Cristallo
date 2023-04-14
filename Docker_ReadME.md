# DTOP-Cristallo
Docker container version of DTOP-Cristallo, developed by the DigiTwin consortium.

## Deployment instructions:

### Pre-requisites
- Ensure that `docker` and `docker compose` are both installed on the deployment machine  
- Clone this repo onto the deployment machine  

### Development deployment
Use this option for deployment on a machine where the certificates are not installed and a http connection is sufficient.  
The app can be deployed using:  
`docker compose up --build -d`

### Notes
- The `--build` flag will (re)build the images before running them run already built images. Omitting this is preferable if you don't need to rebuild the images, but will throw an error if the images don't already exist.  
- The `-d` flag will run the images in detached mode(i.e. as background processes). You may want to omit this for debugging.