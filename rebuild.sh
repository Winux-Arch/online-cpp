#!   /bin/bash -e
podman stop flask-sqlite-app
podman rm flask-sqlite-app
podman build -t flask-sqlite-app .
podman run --name flask-sqlite-app -p 5000:5000 flask-sqlite-app