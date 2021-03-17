#!/bin/bash/
set -o nounset

##################################################################
# Bash script to install kubectl, kubectx, kubens and gcloud SDK #
##################################################################

## Linux/Mac ##
cd /tmp/

## kubectl
echo '###Installing kubectl..'
curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl" && \
chmod +x /tmp/kubectl && \
sudo mv /tmp/kubectl /usr/local/bin/kubectl

###Clone https://github.com/ahmetb/kubectx.. containe kubectx and kubens
sudo git clone https://github.com/ahmetb/kubectx /opt/kubectx
if $? != 0; then
  echo "ERROR: cloning https://github.com/ahmetb/kubectx failed ..."
  exit
fi

## kubectx
echo '###Installing kubectx..'
chmod +x /opt/kubectx/kubectx && \
sudo mv /opt/kubectx/kubectx /usr/local/bin/kubectx
echo "source /opt/kubectx/completion/kubectx.bash" >> ~/.bashrc

## kubens
echo '###Installing kubens..'
chmod +x /opt/kubectx/kubens && \
sudo mv /opt/kubectx/kubens /usr/local/bin/kubens
echo "source /opt/kubectx/completion/kubens.bash" >> ~/.bashrc

## SDK Google
echo '###Installing SDK Google Cloud..'
curl https://sdk.cloud.google.com > install.sh && \
bash install.sh --disable-prompts
