#!/bin/bash/
set -o nounset

##################################################################
# Bash script to install kubectl, kubectx, kubens and gcloud SDK #
#                           LINUX/MAC                            #
##################################################################

cd /tmp/

## kubectl ##
echo '-------> ###Installing kubectl..'
curl -LO "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl" && \
if [ "$?" -ne 0 ]; then
  echo '###ERROR path "https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl" NOT FOUND'
  exit
fi
chmod +x /tmp/kubectl && \
sudo mv /tmp/kubectl /usr/local/bin/kubectl

## kubectx ##
echo '-------> ###Installing kubectx..'
curl -LO "https://raw.githubusercontent.com/ahmetb/kubectx/master/kubectx"
if [ "$?" -ne 0 ]; then
  echo '###ERROR path https://raw.githubusercontent.com/ahmetb/kubectx/master/kubectx NOT FOUND'
  exit
fi
chmod +x /tmp/kubectx && \
sudo mv /tmp/kubectx /usr/local/bin/kubectx

curl -LO "https://raw.githubusercontent.com/ahmetb/kubectx/master/completion/kubectx.bash" && \
echo "source /opt/kubectx/completion/kubectx.bash" >> ~/.bashrc

## kubens ##
echo '-------> ###Installing kubens..'
curl -LO "https://raw.githubusercontent.com/ahmetb/kubectx/master/kubens"
if [ "$?" -ne 0 ]; then
  echo '###ERROR path https://raw.githubusercontent.com/ahmetb/kubectx/master/kubens NOT FOUND'
  exit
fi
chmod +x /tmp/kubens && \
sudo mv /tmp/kubens /usr/local/bin/kubens

curl -LO "https://raw.githubusercontent.com/ahmetb/kubectx/master/completion/kubens.bash" && \
echo "source /opt/kubectx/completion/kubens.bash" >> ~/.bashrc

## SDK Google ##
echo '###Installing SDK Google Cloud..'
curl https://sdk.cloud.google.com > install.sh && \
bash install.sh --disable-prompts &> /dev/null
