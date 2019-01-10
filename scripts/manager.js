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
  .option('-d, --debug', 'Debug', '')
  .option('-e, --environment [type]', 'Define environment', 'development')
  .option('-f, --file [type]', 'Define file', '')

  .parse(process.argv)

const { browser, debug, environment, file, testcafe } = program
const NODE_ENV = environment === 'local' ? 'development' : environment

if (testcafe) {
  const debugOption = debug ? '-d' : ''
  const command = `NODE_ENV=${NODE_ENV} ./node_modules/.bin/testcafe ${browser} ${debugOption} testcafe/${file}`
  childProcess.execSync(command, { stdio: [0, 1, 2] })
}
