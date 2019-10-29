const CaseSensitivePathsPlugin = require('case-sensitive-paths-webpack-plugin')
const eslintFormatter = require('react-dev-utils/eslintFormatter')
const getClientEnvironment = require('./env')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const InterpolateHtmlPlugin = require('react-dev-utils/InterpolateHtmlPlugin')
const path = require('path')
const paths = require('./paths')
const WatchMissingNodeModulesPlugin = require('react-dev-utils/WatchMissingNodeModulesPlugin')
const Webpack = require('webpack')

const publicPath = '/'
const publicUrl = ''
const env = getClientEnvironment(publicUrl)

module.exports = {
  devtool: 'cheap-module-source-map',
  entry: [
    require.resolve('./polyfills'),
    require.resolve('react-dev-utils/webpackHotDevClient'),
    paths.appIndexJs,
  ],
  mode: 'development',
  module: {
    rules: [
      {
        enforce: 'pre',
        include: paths.appSrc,
        test: /\.(js|jsx|mjs)$/,
        use: [
          {
            loader: require.resolve('eslint-loader'),
            options: {
              // https://github.com/webpack-contrib/eslint-loader#emiterror-default-false
              emitError: false,
              emitWarning: true,
              eslintPath: require.resolve('eslint'),
              failOnError: false,
              failOnWarning: false,
              formatter: eslintFormatter,
            },
          },
        ],
      },
      {
        oneOf: [
          {
            loader: require.resolve('url-loader'),
            options: {
              limit: 10000,
              name: 'static/media/[name].[hash:8].[ext]',
            },
            test: [/\.bmp$/, /\.gif$/, /\.jpe?g$/, /\.png$/, /\.ttf$/],
          },
          {
            include: paths.appSrc,
            loader: require.resolve('babel-loader'),
            options: {
              cacheDirectory: true,
            },
            test: /\.(js|jsx|mjs)$/,
          },
          {
            exclude: /node_modules/,
            test: /\.s?css$/,
            use: [
              require.resolve('style-loader'),
              {
                loader: require.resolve('css-loader'),
                options: {
                  importLoaders: 1,
                },
              },
              require.resolve('sass-loader'),
            ],
          },
        ].concat([
          {
            exclude: [/\.js$/, /\.html$/, /\.json$/],
            loader: require.resolve('file-loader'),
            options: {
              name: 'static/media/[name].[hash:8].[ext]',
            },
          },
        ]),
      },
    ],
    strictExportPresence: true,
  },
  node: {
    child_process: 'empty',
    dgram: 'empty',
    fs: 'empty',
    net: 'empty',
    tls: 'empty',
  },
  output: {
    chunkFilename: 'static/js/[name].chunk.js',
    devtoolModuleFilenameTemplate: info =>
      path.resolve(info.absoluteResourcePath).replace(/\\/g, '/'),
    filename: 'static/js/[name].bundle.js',
    pathinfo: true,
    publicPath: publicPath,
  },
  performance: {
    hints: false,
  },
  plugins: [
    new HtmlWebpackPlugin({
      inject: true,
      template: paths.appHtml,
    }),
    new InterpolateHtmlPlugin(HtmlWebpackPlugin, env.raw),
    new Webpack.NamedModulesPlugin(),
    new Webpack.DefinePlugin(env.stringified),
    new Webpack.HotModuleReplacementPlugin(),
    new CaseSensitivePathsPlugin(),
    new WatchMissingNodeModulesPlugin(paths.appNodeModules),
    new Webpack.IgnorePlugin(/^\.\/locale$/, /moment$/),
  ],
  resolve: {
    alias: {
      'react-native': 'react-native-web',
    },
    extensions: ['.web.js', '.mjs', '.js', '.json', '.web.jsx', '.jsx'],
    modules: ['node_modules', paths.appNodeModules].concat(
      process.env.NODE_PATH.split(path.delimiter).filter(Boolean)
    ),
  },
}
