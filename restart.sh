docker stop inventory-app-container 
docker rm inventory-app-container
docker build -t inventory-app .
docker run -d -p 5000:5000 --name inventory-app-container inventory-app