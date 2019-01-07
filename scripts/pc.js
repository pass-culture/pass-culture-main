#!/usr/bin/env node
const childProcess = require('child_process')
const fs = require('fs')
const program = require('commander')
const env = require('node-env-file')
const path = require('path')

const fileDir = path.join(__dirname, '/../env_file')
if (fs.existsSync(fileDir)) {
  env(fileDir)
}

program
  .version('0.1.0')

  .option('testcafe', 'testcafe')

  .option('-b, --browser [type]', 'Define browser', 'chrome')
  .option('-e, --environment [type]', 'Define environment', 'development')
  .option('-f, --file [type]', 'Define file', '')

  .parse(process.argv)

const { browser, environment, file, testcafe } = program
const NODE_ENV = environment === 'local' ? 'development' : environment

if (testcafe) {
  const debugOption = program.environment === 'local' ? '-d' : ''
  const command = `NODE_ENV=${NODE_ENV} ./node_modules/testcafe/bin/testcafe.js ${browser} ${debugOption} testcafe/${file}`
  childProcess.execSync(command, { stdio: [0, 1, 2] })
}
