const fs = require('fs')
const url = require('url')
const path = require('path')

// Make sure any symlinks in the project folder are resolved:
// https://github.com/facebookincubator/create-react-app/issues/637
const appDirectory = fs.realpathSync(process.cwd())
const resolveApp = relativePath => path.resolve(appDirectory, relativePath)

const envPublicUrl = process.env.PUBLIC_URL

function ensureSlash(ppath, needsSlash) {
  const hasSlash = ppath.endsWith('/')
  if (hasSlash && !needsSlash) {
    return ppath.substr(ppath, ppath.length - 1)
  }
  if (!hasSlash && needsSlash) {
    return `${ppath}/`
  }
  return ppath
}

const getPublicUrl = appPackageJson => envPublicUrl || require(appPackageJson).homepage

// We use `PUBLIC_URL` environment variable or "homepage" field to infer
// "public path" at which the app is served.
// Webpack needs to know it to put the right <script> hrefs into HTML even in
// single-page apps that may serve index.html for nested URLs like /todos/42.
// We can't use a relative path in HTML because we don't want to load something
// like /todos/42/static/js/bundle.7289d.js. We have to know the root.
function getServedPath(appPackageJson) {
  const publicUrl = getPublicUrl(appPackageJson)
  const servedUrl = envPublicUrl || (publicUrl ? url.parse(publicUrl).pathname : '/')
  return ensureSlash(servedUrl, true)
}

// config after eject: we're in ./config/
module.exports = {
  appBuild: resolveApp('build'),
  appHtml: resolveApp('public/index.html'),
  appIndexJs: resolveApp('src/index.jsx'),
  appNodeModules: resolveApp('node_modules'),
  appPackageJson: resolveApp('package.json'),
  appPublic: resolveApp('public'),
  appSrc: resolveApp('src'),
  dotenv: resolveApp('.env'),
  publicUrl: getPublicUrl(resolveApp('package.json')),
  servedPath: getServedPath(resolveApp('package.json')),
  testsSetup: resolveApp('src/setupTests.js'),
  yarnLockFile: resolveApp('yarn.lock'),
}
