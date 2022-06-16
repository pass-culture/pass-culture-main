/* eslint-disable @typescript-eslint/no-var-requires */
const SentryWebpackPlugin = require('@sentry/webpack-plugin')
const { config } = require('dotenv')

const pkg = require('./package.json')

const { parsed: env } = config()

module.exports = {
  webpack(config, webpackEnv) {
    const isEnvProduction = webpackEnv === 'production'
    return {
      ...config,
      plugins: [
        ...config.plugins,
        isEnvProduction &&
          new SentryWebpackPlugin({
            include: 'build',
            rewrite: true,
            release: pkg.version,
            dist: pkg.version,
            cleanArtifacts: false,
            finalize: env.REACT_APP_ENV !== 'testing',
            deploy: {
              env: env.REACT_APP_ENV,
              name: env.REACT_APP_ENV,
              url: env.REACT_APP_URL_BASE,
            },
          }),
      ].filter(Boolean),
    }
  },
}
