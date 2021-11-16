const path = require('path')
const configPaths = require('../config/paths')

function resolve(dir) {
  return path.join(__dirname, dir)
}

const aliases = {
  components: resolve('../src/components'),
  new_components: resolve('../src/new_components'),
  'ui-kit': resolve('../src/ui-kit'),
  styles: resolve('../src/styles'),
  images: resolve('../src/images'),
  screens: resolve('../src/screens'),
  icons: resolve('../src/icons'),
  utils: resolve('../src/utils'),
}

const sassResourcesLoader = {
  loader: 'sass-resources-loader',
  options: {
    hoistUseStatements: true,
    resources: [
      path.resolve(configPaths.appSrc, './styles/variables/index.scss'),
      path.resolve(configPaths.appSrc, './styles/mixins/index.scss'),
    ],
  },
}

module.exports = {
  stories: ['../src/**/*.stories.mdx', '../src/**/*.stories.@(js|jsx|ts|tsx)'],
  addons: [
    '@storybook/addon-links',
    '@storybook/addon-essentials',
    'storybook-svgr-react-component',
    '@storybook/addon-a11y',
  ],
  webpackFinal: config => {
    config.module.rules.push({
      test: /\.scss$/,
      use: [
        'style-loader',
        'css-loader',
        {
          loader: 'resolve-url-loader',
          options: {
            sourceMap: true,
            root: configPaths.appSrc,
          },
        },
        'sass-loader',
        sassResourcesLoader,
      ],
      include: path.resolve(__dirname, '../'),
    })

    return {
      ...config,
      resolve: {
        ...config.resolve,
        alias: {
          ...config.resolve?.alias,
          ...aliases,
        },
      },
    }
  },
}
