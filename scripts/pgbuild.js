'use strict';

const archiver = require('archiver');
const { exec } = require('child_process')
const fs = require('fs');
const pgb_client = require('phonegap-build-api');

const APP_IDS = {'prod' : 3048468, 'staging' : 3059566 }

const ENV = process.env.PG_ENV || 'staging'

const APP_ID = APP_IDS[ENV]

const PGB_LOGIN = process.env.PQ_PGB_LOGIN
const PGB_PASSWORD = process.env.PQ_PGB_PASSWORD


if (!PGB_LOGIN || !PGB_PASSWORD) {
  console.log("Environment variables PQ_PGB_LOGIN and PQ_PGB_PASSWORD need to be set to your Phonegap Build credentials")
  process.exit()
}

function pgb_do(callback) {
  pgb_client.auth({ username: PGB_LOGIN, password: PGB_PASSWORD },
                  callback);
}


function createZipOrPushGit() {
  if (ENV === 'staging') {
    console.log('Pushing build to Github staging repo');
      const packed_dir = `"${__dirname}/../../webapp-packed-staging/"`
      exec(`git checkout master;
            cp -r "${__dirname}/../build/"* ${packed_dir};
            mv "${__dirname}/../pg_config_staging.xml ${packed_dir}/config.xml";
            git commit -am "Automated commit";
            git push origin master`,
           function (error, stdout, stderr)
             {
             if (error) {
               console.error(error);
               process.exit(1)
             }
             console.log(stdout);
             console.error(stderr);
             triggerBuild();
             });
        
  } else {
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
}

function triggerBuild() {
  pgb_do(function(e, api) {
    api.post('/apps/'+APP_ID+'/build',
             function(e, data) {
               console.log('error:', e);
               console.log('data:', data);
               if (!e) {
                  monitorBuild()
               }
             });
  });
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
           api.put('/apps/'+APP_ID, options,
                   function(e, data) {
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
           api.get('/apps/'+APP_ID, function(e, data) {
               console.log('error:', e);
               console.log('data:', data);
               if (data.status.android === 'pending') {
                   console.log('Waiting for Android build')
                   setTimeout(monitorBuild, 1000);
               } else if (data.status.android === 'error') {
                   console.log('PGB android build failed, check build log : https://build.phonegap.com/apps'+APP_ID+'/logs/android/build/')
               } else {
                   console.log('PGB android build DONE')
               }
           })
         });
}

function downloadApps() {
  pgb_do(function(e, api) {
           api.get('/apps/'+APP_ID+'/android', function(e, data) {
             console.log('Downloading android app')
             fs.writeFileSync('android.apk', data, 'binary');
         });
       });
}

createZipOrPushGit();
