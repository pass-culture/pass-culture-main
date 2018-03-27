#!/bin/bash

# SCRIPT D'INITIALISATION D'UN SERVEUR SUR LA BASE DE L'IMAGE ARCHLINUX OVH PUBLIC CLOUD

function start-docker {
  screen -d -m docker-compose up --force-recreate
  screen -rd -p 0 -X log on
  tail -f screenlog.0 | sed '/Debugger is active/ q' # FIXME: get some other clue that the server is started !
}

echo "/!\ before you run this script, please run: "
echo "$ sudo pacman -Suy"
echo "$ sudo reboot"

read -p "HOSTNAME (Ex: docker-host-prod): " HOSTNAME
read -p "FQDN FOR NGINX (Ex: api.passculture.beta.gouv.fr): " FQDN

echo "HOSTNAME will be $HOSTNAME"
echo "FQDN will be $FQDN"
read -p "Is this correct ? (y/n) " -n 1 reply >&2
if [[ ! $reply = "Y" ]] && [[ ! $reply = "y" ]]; then
  exit 1
fi

sudo hostnamectl set-hostname "$HOSTNAME"

sudo pacman -S dnsutils moreutils git ntp screen wget

sudo systemctl start ntpd
sudo systemctl enable ntpd

sudo useradd deploy
sudo passwd -l deploy
sudo mkdir /home/deploy
sudo chown deploy /home/deploy
sudo usermod -a -G wheel deploy
sudo cat /etc/sudoers | sed -e 's|# %wheel ALL=(ALL) NOPASSWD: ALL|%wheel ALL=(ALL) NOPASSWD: ALL|' | sudo EDITOR='tee -a' visudo

sudo -E su deploy
cd

mkdir ~/.ssh
chown o-rwx ~/.ssh
chown g-rwx ~/.ssh
touch ~/.ssh/authorized_keys
echo "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAsbMptXdns+vGlapjXzoff7r9j+i0iHtVW8ZlEDbeU/dfcp3J1YpyY+2ubVsiJqfim5AIBZMr4IEaKedH0aaJqKyP1mTIup8RcK27Ri7gmhvr9RDbyPTbIsrO/ijYQrqIXB6DUEaPY/DZIAD7SQK7rJ7r5joBAaqxxhknhUqwv2vzL8+1GUKeg5ANHZ+2yl5dKW3t+MzB5Wf6Z3+NhkSMhnEpt82RWNZY6iPBlth6z4t4KnVH4XTXqg99hpVvzIJPeQduft0gwgXOQPoK9//NM1dBhuj/fxoLQuW8slrA8lYEt3nhttPrJ8mgt9RAvjFHhfE2BmhP5+P8oIHyU3LpEQ== Arnaud" >> ~/.ssh/authorized_keys
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC+cKCqDRewBQlz7G6fBYuCTS4khN3fjOKq2DNyfI0DAfCcJmTSaCTYrNUKmPqNklf0gIUgxGudvHRuBpdzdqzVW7xhsPHWCNpHtJJjVwNcZV54F62cNgdmeOzRGuWSJ3k92uS+V4pz/yOUhQlZCsU4Oqt8S3oXVc0p90SXuTUWt2FabaYCf2gi9axLq31VSFvVCS+I9X9ev4si4EKrvY3LPCYKFjoZLOoSad9eyFRXElK3SBf1tdez17jUYRXf0n/uo9ZRNmco4jp1Avjh+XhKXRXEtYaRHxYIkqtaCCfAPG1gKiqnUoMwaIjykwXfUR5tfWbBYqNR4/yxLXVICQzz Erwan" >> ~/.ssh/authorized_keys
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC0j45qbtAeutTXOHurfBlnORa2/b7YXI+IoOHbP4aCnrgzf9xdZIgHQChqUA6yEo///IdJEw5TPJxqsVDcfMX+Qyrpn1HDasgPcUNYpo2tuXA641MV6JlAqdKxeXjb0RAxfJUKKpbml7wg66twnNBS7llpT0sjDl+uCoCQ4GkNT65SvsyeYke6duVM/plAq4ghX1Qe0w8+vk/td0smUZBxE5R38ouUwUV20Oc/GZxG5us70ay+EgTmEFR0WmN2bEt8Ff9borx4CLB6GoAsbd4Jp2ITsRdCGibr7G3y/kwYFyJffrJ8moIlVXq7JyQF7s+ZsllNN02xqr9f8AhUwUsCudn+a2UbGM9fNycqNemDIIhk7gioZx7cBvrSvGrXcK5muNzAF9lIkNdKbAR3Ed2b74XYOe8aGHSufJku6bYJhsw/bgb/fick4PJnQhzfeBd+E6EDgXHB4EDWesIrh9tHj55vkifpoU0yooHwPtCBtkSVp6Wimie3Kv9dD+lbjBSBc1Hd5t9AeVYf2ssgWrOMSgRIQkNQL+E1wjId3qXq2tdAZvolZnK6E1ioMKZmPEP2ALwILBuRN4IK0HT4lFQ+rt25lSu9MpF/GZLfiEmLsKrrAaXm42NO4DZpoYeo43uSWC0co44TbY5PEHbZU7iisDZCX9wqH7eSSXwXxJReFw== Augustin" >> ~/.ssh/authorized_keys

git clone https://github.com/betagouv/pass-culture-main
cd pass-culture-main 
sed -i -e 's#git@github.com:#https://github.com/#' .gitmodules
git submodule init
git submodule update
git submodule foreach git checkout master


sudo pacman -S certbot certbot-nginx cronie docker-compose docker lftp unzip
sudo usermod -a -G docker deploy
exec su -l deploy

cd ~/pass-culture-main 

sudo systemctl start docker
sudo systemctl enable docker

start-docker

docker run -it --rm -v ~/pass-culture-main/certs:/etc/letsencrypt -v ~/pass-culture-main/certs-data:/data/letsencrypt deliverous/certbot certonly --verbose --webroot --webroot-path=/data/letsencrypt -d "$FQDN" --agree-tos -m "arnaud.betremieux@beta.gouv.fr" -n

sudo systemctl start cronie
sudo systemctl enable cronie
crontab -l | { cat; echo "0 0 * * * docker run -it --rm -v ~/pass-culture-main/certs:/etc/letsencrypt -v ~/pass-culture-main/certs-data:/data/letsencrypt deliverous/certbot renew --verbose --webroot --webroot-path=/data/letsencrypt"; } | crontab -

cd dockerfiles/nginx/conf.d
sed -i -e 's/##FQDN##/'"$FQDN"'/' flaskapp_ssl
ln -sf flaskapp_ssl flaskapp.conf
cd -
docker-compose down
start-docker
echo "ALL DONE. Run pc test-backend to check install, then maybe some other form of DB init."
