'use strict';

var archiver = require('archiver');
var file_system = require('fs');
var pgb_client = require('phonegap-build-api');

const PGB_LOGIN=process.env.PQ_PGB_LOGIN
const PGB_PASSWORD=process.env.PQ_PGB_PASSWORD

if (!PGB_LOGIN || !PGB_PASSWORD) {
  console.log("Environment variables PGB_LOGIN and PGB_PASSWORD need to be set to your Phonegap Build credentials")
  process.exit()
}


function createZip() {
  console.log('Zipping build for PG Build');
  var output = file_system.createWriteStream('target.zip');
  var archive = archiver('zip');
  
  output.on('close', function () {
      console.log('Build zipped');
      uploadToPGB('target.zip')
  });
  
  archive.on('error', function(err){
      throw err;
  });
  
  archive.pipe(output);
  archive.file('pg_config.xml', { name: 'config.xml' });
  archive.glob('**/**', {cwd: 'build'});
  archive.finalize();
}

function uploadToPGB(zipfile) {
  pgb_client.auth({ username: PGB_LOGIN, password: PGB_PASSWORD },
                  function(e, api) {
                     var options = {
                         form: {
                             data: {
                                 debug: false
                             },
                             file: zipfile
                         }
                     };
                     
                     api.put('/apps/3048468', options, function(e, data) {
                         console.log('error:', e);
                         console.log('data:', data);
                     })
                   });
}

createZip();
