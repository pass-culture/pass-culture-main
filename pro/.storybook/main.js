const path = require('path')
const webpack = require('webpack')

function resolve(dir) {
  return path.join(__dirname, dir)
}

const aliases = {
  core: resolve('../src/core'),
  components: resolve('../src/components'),
  new_components: resolve('../src/new_components'),
  hooks: resolve('../src/hooks'),
  'ui-kit': resolve('../src/ui-kit'),
  styles: resolve('../src/styles'),
  images: resolve('../src/images'),
  screens: resolve('../src/screens'),
  icons: resolve('../src/icons'),
  utils: resolve('../src/utils'),
  custom_types: resolve('../src/custom_types'),
  repository: resolve('../src/repository'),
  hooks: resolve('../src/hooks'),
}

module.exports = {
  core: {
    builder: 'webpack5',
  },
  stories: ['../src/**/*.stories.@(js|jsx|ts|tsx|mdx)'],
  addons: [
    'storybook-svgr-react-component',
    '@storybook/addon-docs',
    '@storybook/addon-actions',
    '@storybook/addon-links',
    {
      name: '@storybook/addon-essentials',
      options: {
        // https://github.com/storybookjs/storybook/issues/15901
        // docs not compatible with webpack 5.
        docs: false,
      },
    },
  ],
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
    config.module.rules.push({
      test: /\.svg$/,
      include: path.resolve(__dirname, '../src'),
      use: [
        {
          loader: '@svgr/webpack',
          options: {
            icon: true,
          },
        },
      ],
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
