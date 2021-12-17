'use strict'

const { version } = require('../package.json')
const { readFileSync, writeFileSync } = require('fs')
const { join } = require('path')

// Set your env with DISABLE_V1_TO_V2_REDIRECT=true to disable Web App v1 to v2 redirect
process.env.DISABLE_V1_TO_V2_REDIRECT = process.env.DISABLE_V1_TO_V2_REDIRECT || 'false'

// Do this as the first thing so that any code reading it knows the right env.
process.env.NODE_ENV = process.env.NODE_ENV || 'development'

const indexHTMLFilePath = join(__dirname, '../build/index.html')
const publicRedirectFilePath = join(__dirname, '../public/_redirects')
const redirectFilePath = join(__dirname, '../build/_redirects')
const versionTxtPath = join(__dirname, '../build/version.txt')

// Makes the script crash on unhandled rejections instead of silently
// ignoring them. In the future, promise rejections that are not handled will
// terminate the Node.js process with a non-zero exit code.
process.on('unhandledRejection', err => {
  throw err
})

// Ensure environment variables are read.
require('../config/env')

function createRedirectFile() {
  try {
    const disableV1ToV2Redirect = JSON.parse(process.env.DISABLE_V1_TO_V2_REDIRECT)

    console.log(
      `Building redirects for ${process.env.NODE_ENV}`,
      disableV1ToV2Redirect ? '' : `, Web App v2 URL: ${process.env.WEBAPP_V2_URL}`,
    )

    const publicRedirectFileContent = readFileSync(publicRedirectFilePath, 'utf8')
    const JSpath = `/${readFileSync(indexHTMLFilePath, 'utf8').match(/static\/js\/main\.[a-z0-9]*\.js/g)[0]}`

    const assets = [
      ['/static/js/*', JSpath, '301'],
      ['/:path1/static/js/*', JSpath, '301'],
      ['/:path1/:path2/static/js/*', JSpath, '301'],
      ['/:path1/:path2/:path3/static/js/*', JSpath, '301'],
      ['/:path1/:path2/:path3/:path4/static/js/*', JSpath, '301'],
      ['/:path1/:path2/:path3/:path4/:path5/static/js/*', JSpath, '301'],
      ['/:path1/:path2/:path3/:path4/:path5/:path6/static/js/*', JSpath, '301'],
      ['/static/css/*', JSpath, '301'],
      ['/:path1/static/css/*', JSpath, '301'],
      ['/:path1/:path2/static/css/*', JSpath, '301'],
      ['/:path1/:path2/:path3/static/css/*', JSpath, '301'],
      ['/:path1/:path2/:path3/:path4/static/css/*', JSpath, '301'],
      ['/:path1/:path2/:path3/:path4/:path5/static/css/*', JSpath, '301'],
      ['/:path1/:path2/:path3/:path4/:path5/:path6/static/css/*', JSpath, '301'],
    ]

    const v1 = publicRedirectFileContent.match(/.*\n/g, '').map((line) => line.replace(/\n/, '').split(' ').filter((arr) => arr.length > 1))

    const v1tov2 = [
      ['/version.txt', '/version.txt', '200'],
      ['/accueil/details/:offerId', '/accueil/details/:offerId', '200'],
      ['/*', process.env.WEBAPP_V2_URL, '302!'],
    ]

    let content = ''

    // eslint-disable-next-line no-extra-boolean-cast
    const redirects = disableV1ToV2Redirect ? [...assets, ...v1] : [...assets, ...v1tov2]

    redirects.forEach((asset) => {
      content += `${asset[0]} ${asset[1]} ${asset[2]}\n`
    })

    writeFileSync(redirectFilePath, content, 'utf8')
    console.log(`Redirects created:\n${readFileSync(redirectFilePath, 'utf8')}`)

    writeFileSync(versionTxtPath, version, 'utf8')
    console.log('Version copied to version.txt.')
  } catch (error) {
    console.error(error)
  }
}

createRedirectFile()
