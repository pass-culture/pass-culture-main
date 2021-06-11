const path = require('path');
const configPaths = require('../config/paths')

function resolve(dir) {
  return path.join(__dirname, dir)
}

const aliases = {
  'components': resolve('../src/components'),
  'styles': resolve('../src/styles'),
  'images': resolve('../src/images'),
  'icons': resolve('../src/icons'),
}

module.exports = {
  "stories": [
    "../src/**/*.stories.mdx",
    "../src/**/*.stories.@(js|jsx|ts|tsx)"
  ],
  "addons": [
    "@storybook/addon-links",
    "@storybook/addon-essentials",
    "storybook-svgr-react-component",
  ],
   "webpackFinal": (config) => {
     config.module.rules.push(
      {
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
          'sass-loader'
        ],
        include: path.resolve(__dirname, '../'),
      },
    );

    return {
     ...config,
      resolve: {
        ...config.resolve,
        alias: {
          ...config.resolve?.alias,
          ...aliases,
        },
      }
    }
  },
}