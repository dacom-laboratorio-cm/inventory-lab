sudo docker stop inventory-app-container 
sudo docker rm inventory-app-container
sudo docker build -t inventory-app .
sudo docker run -d --restart unless-stopped -p 5000:5000 --name inventory-app-container inventory-app