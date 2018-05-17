'use strict';

(() => {
  const archiver = require('archiver');
  const { exec } = require('child_process')
  const fs = require('fs');
  const env = require('node-env-file');
  const path =  require('path');
  const util = require('util');
  require('util.promisify').shim();
  const { promisify } = util
  const pgb_client = require('phonegap-build-api');
  const request = require('request');


  const fileDir = path.join(__dirname, '/../env_file')
  if (fs.existsSync(fileDir)) { env(fileDir) }

  const APP_IDS = {
    production: 3110560,
    staging: 3059566
  }

  const PG_ENV = process.env.PG_ENV || 'staging'
  const PQ_PGB_LOGIN = process.env.PQ_PGB_LOGIN
  const PQ_PGB_PASSWORD = process.env.PQ_PGB_PASSWORD
  const APP_ID = APP_IDS[PG_ENV]

  const raiseAndKill = msg => error => {
    console.error(msg);
    if (error) console.error(error);
    process.exit(1);
  }

  if (!PQ_PGB_LOGIN || !PQ_PGB_PASSWORD)
    raiseAndKill('Environment variables PQ_PGB_LOGIN and PQ_PGB_PASSWORD '+
                  'need to be set to your Phonegap Build credentials')();

  const pgb_do = () => promisify(pgb_client.auth)({
      username: PQ_PGB_LOGIN,
      password: PQ_PGB_PASSWORD,
  }).catch(raiseAndKill('Phonegap API authentication error'))

  const addCordovaJsToIndexHtml = () => {
    const indexHtml = `${__dirname}/../build/index.html`
    return new Promise((resolve, reject) => {
      fs.readFile(indexHtml, 'utf8', function (err, content) {
        if (err) reject(err)
        var newContent = content.replace(/<body>/, '<body><script type="text/javascript" src="cordova.js"></script>');
        fs.writeFile(indexHtml, newContent, 'utf8', function (err) {
           if (err) reject(err);
           resolve();
        });
      });
    })
  }

  const pushToGit = () => {
    console.log('Pushing build to Github staging repo');
    const packed_dir = `${__dirname}/../../webapp-packed-staging/`
    return promisify(exec)(`
      rm -rf ${packed_dir}/static/js ${packed_dir}/static/css
      cp -r ${__dirname}/../build/* ${packed_dir};
      cp ${__dirname}/../config-${PG_ENV}.xml ${packed_dir}/config.xml;
      cd ${packed_dir};
      sed -i -e 's#https://api.passculture.beta.gouv.fr#https://api.passculture-staging.beta.gouv.fr#' static/js/*.js
      git checkout master;
      git add .;
      git commit -am "Automated commit";
      git push --force origin master;
      cd -;
    `).then(({stdout, stderr}) => {
      if (stderr) console.error(stderr);
      console.log(stdout);
    }).catch(raiseAndKill('Error while executing commands'))

  };

  const createZip = () => new Promise((resolve, reject) => {
    console.log('Zipping build for PG Build');
    let output = fs.createWriteStream('target.zip');

    output.on('close', () => {
      console.log('Build zipped');
      resolve();
    })

    let archive = archiver('zip');
    archive.on('error', raiseAndKill('Could not build archive'));
    archive.pipe(output);
    archive.file(`config-${PG_ENV}.xml`, { name: 'config.xml' });
    archive.glob('**/**', {cwd: 'build'});
    archive.finalize();
  })

  const triggerGithubBuild = () => {
    const options = {
      url: `https://build.phonegap.com/apps/${APP_ID}/push`,
      auth: {
        user: PQ_PGB_LOGIN,
        password: PQ_PGB_PASSWORD
      }
    };

    return promisify(request)(options)
      .then((res, body) => {
        return console.dir(body);
      }).catch(raiseAndKill('Could not trigger build'))
  }

  const uploadToPGB = () => pgb_do()
    .then(api => {
      const options = {
        form: {
          data: {
            debug: false
          },
          file: 'target.zip'
        }
      };
      return promisify(api.put)(`/apps/${APP_ID}`, options)
        .then(data => console.log('Upload result data:', data))
        .catch(raiseAndKill('Could not send to PGB'))
    });

  const monitorBuild = () => new Promise((resolve, reject) => {
    const checkLoop = () => pgb_do()
      .then(api => promisify(api.get)(`/apps/${APP_ID}`))
      .then(data => {
        if (data.status.android === 'pending') {
          console.log('Waiting for Android build, retrying in 1 second')
          setTimeout(checkLoop, 1000);
        } else if (data.status.android === 'error') {
          reject(data);
        } else {
          resolve(data);
        }
      });
    checkLoop();
  });

  const downloadApk = () => pgb_do()
    .then(api => promisify(api.get)(`/apps/${APP_ID}/android`))
    .then(data => {
      console.log('Downloading android app')
      fs.writeFileSync('android.apk', data, 'binary');
    });

  const main = () => {
    return addCordovaJsToIndexHtml()
      .then(() => {
        if (PG_ENV === 'staging') {
          return pushToGit()
            .then(() => triggerGithubBuild())
        } else {
          return createZip()
            .then(() => uploadToPGB())
        }
      })
      .then(() => monitorBuild())
      .then(data => console.log(`${PG_ENV} PGB Android build SUCCESS`, data))
      .then(() => downloadApk())
      .catch(error => console.error(`${PG_ENV} PGB Android build FAILED`, error))
  }

  main();
})();
