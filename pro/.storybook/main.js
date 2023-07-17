const path = require('path')
const webpack = require('webpack')
function resolve(dir) {
  return path.join(__dirname, dir)
}
const aliases = {
  core: resolve('../src/core'),
  components: resolve('../src/components'),
  hooks: resolve('../src/hooks'),
  'ui-kit': resolve('../src/ui-kit'),
  styles: resolve('../src/styles'),
  images: resolve('../src/images'),
  screens: resolve('../src/screens'),
  icons: resolve('../src/icons'),
  utils: resolve('../src/utils'),
  custom_types: resolve('../src/custom_types'),
  repository: resolve('../src/repository'),
}
module.exports = {
  stories: ['../src/**/*.stories.@(js|jsx|ts|tsx|mdx)'],
  addons: ['@storybook/addon-a11y'],
  staticDirs: ['../public'],
  plugins: [
    new webpack.DefinePlugin({
      'process.env': {},
      'process.env.NODE_ENV': JSON.stringify('development'),
      'process.env.FLAG': JSON.stringify('false'),
    }),
  ],
  webpackFinal: config => {
    config.module.rules.push({
      test: /\.scss$/,
      use: [
        'style-loader',
        {
          loader: 'css-loader',
          options: {
            importLoaders: 1,
            modules: {
              localIdentName: '[name]__[local]___[hash:base64:5]',
            },
          },
        },
        'resolve-url-loader',
        'sass-loader',
      ],
      include: path.resolve(__dirname, '../src'),
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
  framework: {
    name: '@storybook/react-webpack5',
    options: {},
  },
  docs: {
    autodocs: true,
  },
}
