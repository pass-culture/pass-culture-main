# unfortunately the --watch does not work apparently
pid=$(lsof -i TCP:3001 | grep LISTEN | awk '{print $2}')
if [ ! -z $pid ]; then
  kill -9 $pid;
fi
drakov -f ./apiary.apib.md -p 3001 --autoOptions --header Authorization
