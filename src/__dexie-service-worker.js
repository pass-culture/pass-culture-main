import { db, pull } from './utils/dexie'

function send_message_to_client(client, msg){
    return new Promise(function(resolve, reject){
        var msg_chan = new MessageChannel();

        msg_chan.port1.onmessage = function(event){
            if(event.data.error){
                reject(event.data.error);
            }else{
                resolve(event.data);
            }
        };

        client.postMessage("SW Says: '"+msg+"'", [msg_chan.port2]);
    });
}

function send_message_to_all_clients(msg){
    clients.matchAll().then(clients => {
        clients.forEach(client => {
            send_message_to_client(client, msg).then(m => console.log("SW Received Message: "+m));
        })
    })
}

self.addEventListener('sync', function (event) {
  if (event.tag === 'dexie-pull') {
    console.log('event.ta', event.tag)
    db.configs.add({ id: Math.random() }).then((f) => {
      console.log('f', f)
      send_message_to_all_clients('Hello ' + f)
    })
    // event.waitUntil(pull)
  }
})
