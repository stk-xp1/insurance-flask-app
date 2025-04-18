 podman build -t flask-app . 
podman run -p 5000:5000 flask-app
podman run -p 5000:5000 --name myflaskapp flask-app
