'use strict';

var archiver = require('archiver');
var fs = require('fs');
var pgb_client = require('phonegap-build-api');
const { exec } = require('child_process')

const PGB_LOGIN=process.env.PQ_PGB_LOGIN
const PGB_PASSWORD=process.env.PQ_PGB_PASSWORD

if (!PGB_LOGIN || !PGB_PASSWORD) {
  console.log("Environment variables PGB_LOGIN and PGB_PASSWORD need to be set to your Phonegap Build credentials")
  process.exit()
}

function pgb_do(callback) {
  pgb_client.auth({ username: PGB_LOGIN, password: PGB_PASSWORD },
                  callback);
}


function createZip() {
  console.log('Zipping build for PG Build');
  var output = fs.createWriteStream('target.zip');
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
  pgb_do(function(e, api) {
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
               if (!e) {
                  monitorBuild()
               }
           })
         });
}

function monitorBuild() {
  pgb_do(function(e, api) {
           api.get('/apps/3048468', function(e, data) {
               console.log('error:', e);
               console.log('data:', data);
               if (data.status.android === 'pending') {
                   console.log('Waiting for Android build')
                   setTimeout(monitorBuild, 1000);
               } else if (data.status.android === 'error') {
                   console.log('PGB android build failed, check build log : https://build.phonegap.com/apps/3048468/logs/android/build/')
               } else {
                   downloadApps()
               }
           })
         });
}

function downloadApps() {
  pgb_do(function(e, api) {
           api.get('/apps/3048468/android', function(e, data) {
             console.log('Downloading android app')
             fs.writeFileSync('android.apk', data, 'binary');
         });
       });
}

createZip();
