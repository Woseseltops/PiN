#!/bin/bash
echo "Content-type: text/plain"
echo
echo "Deployment started..."
sudo /var/www/repo/deploy-as-root.sh 
echo "Success"
