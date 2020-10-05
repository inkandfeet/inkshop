#! /bin/sh
while true; do
    read -p "Have you committed all changes in inkshop?  Ready for everything to be overwritten? " yn
    case $yn in
        [Yy]* ) rsync -ac --progress ../inkandfeet-inkshop/ ../inkshop --exclude .git  --exclude .pyc --exclude .DS_Store; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done

