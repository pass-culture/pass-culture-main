const Autoprefixer = require('autoprefixer')
const CopyWebpackPlugin = require('copy-webpack-plugin')
const getClientEnvironment = require('./env')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const HtmlCriticalWebpackPlugin = require('html-critical-webpack-plugin')
const InterpolateHtmlPlugin = require('react-dev-utils/InterpolateHtmlPlugin')
const ManifestPlugin = require('webpack-manifest-plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const ModuleScopePlugin = require('react-dev-utils/ModuleScopePlugin')
const SWPrecacheWebpackPlugin = require('sw-precache-webpack-plugin')
const PostCssFlexbugsFixes = require('postcss-flexbugs-fixes')
const path = require('path')
const paths = require('./paths')
const TerserPlugin = require('terser-webpack-plugin')
const Webpack = require('webpack')

const publicPath = paths.servedPath
const shouldUseSourceMap = process.env.GENERATE_SOURCEMAP !== 'false'
const publicUrl = publicPath.slice(0, -1)
const env = getClientEnvironment(publicUrl)

if (env.stringified['process.env'].NODE_ENV !== '"production"') {
  throw new Error('Production builds must have NODE_ENV=production.')
}

module.exports = {
  bail: true,
  devtool: shouldUseSourceMap ? 'source-map' : false,
  entry: [require.resolve('./polyfills'), paths.appIndexJs],
  mode: 'production',
  module: {
    strictExportPresence: true,
    rules: [
      {
        oneOf: [
          {
            loader: 'url-loader',
            options: {
              limit: 10000,
              name: 'static/media/[name].[hash:8].[ext]',
            },
            test: [/\.bmp$/, /\.gif$/, /\.jpe?g$/, /\.png$/, /\.ttf$/],
          },
          {
            exclude: process.env.HAS_WORKERS && /index\.(.*)\.worker\.js$/,
            include: paths.appSrc,
            loader: 'babel-loader',
            options: {
              compact: true,
            },
            test: /\.(js|jsx|mjs)$/,
          },
          {
            test: /\.s?css$/,
            exclude: /node_modules/,
            use: [
              MiniCssExtractPlugin.loader,
              {
                loader: 'css-loader',
                options: {
                  importLoaders: 1,
                  sourceMap: shouldUseSourceMap,
                },
              },
              {
                loader: 'postcss-loader',
                options: {
                  ident: 'postcss',
                  plugins: () => [
                    PostCssFlexbugsFixes,
                    Autoprefixer({
                      flexbox: 'no-2009',
                      overrideBrowserslist: ['>1%', 'last 4 versions', 'Firefox ESR', 'not ie < 9'],
                    }),
                  ],
                },
              },
              {
                loader: 'sass-loader',
              },
            ],
          },
        ]
          .concat(
            process.env.HAS_WORKERS
              ? [
                {
                  loader: 'worker-loader',
                  options: { inline: true },
                  test: /index\.(.*)\.worker\.js$/,
                },
              ]
              : []
          )
          .concat([
            {
              exclude: [/\.js$/, /\.html$/, /\.json$/],
              loader: 'file-loader',
              options: {
                name: 'static/media/[name].[hash:8].[ext]',
              },
            },
          ]),
      },
    ],
  },
  node: {
    dgram: 'empty',
    fs: 'empty',
    net: 'empty',
    tls: 'empty',
    child_process: 'empty',
  },
  optimization: {
    runtimeChunk: 'single',
    minimize: true,
    minimizer: [new TerserPlugin()],
    splitChunks: {
      chunks: 'all'
    }
  },
  output: {
    chunkFilename: 'static/js/[name].[chunkhash:8].js',
    filename: 'static/js/[name].[chunkhash:8].js',
    devtoolModuleFilenameTemplate: info =>
      path.relative(paths.appSrc, info.absoluteResourcePath).replace(/\\/g, '/'),
    path: paths.appBuild,
    publicPath,
  },
  performance: {
    maxAssetSize: 2000000,
    maxEntrypointSize: 3000000,
  },
  plugins: [
    new CopyWebpackPlugin(
      ['bmp', 'pdf', 'jpg', 'jpeg', 'png'].map(extension => ({
        from: path.resolve(`${paths.appPublic}/**/*.${extension}`),
        to: path.resolve(`${paths.appBuild}/**/*.${extension}`),
      }))
    ),
    new HtmlWebpackPlugin({
      inject: true,
      template: paths.appHtml,
      minify: {
        collapseWhitespace: true,
        keepClosingSlash: true,
        minifyCSS: true,
        minifyJS: true,
        minifyURLs: true,
        removeComments: true,
        removeRedundantAttributes: true,
        removeEmptyAttributes: true,
        removeStyleLinkTypeAttributes: true,
        useShortDoctype: true,
      },
    }),
    new InterpolateHtmlPlugin(HtmlWebpackPlugin, env.raw),
    new MiniCssExtractPlugin({
      chunkFilename: '[id].css',
      filename: '[name].css',
    }),
    new Webpack.DefinePlugin(env.stringified),
    new ManifestPlugin({
      fileName: 'asset-manifest.json',
    }),
    new SWPrecacheWebpackPlugin({
      dontCacheBustUrlsMatching: /\.\w{8}\./,
      filename: 'service-worker.js',
      logger(message) {
        if (message.indexOf('Total precache size is') === 0) {
          return
        }
        if (message.indexOf('Skipping static resource') === 0) {
          return
        }
      },
      minify: true,
      navigateFallback: `${publicUrl}/index.html`,
      navigateFallbackWhitelist: [/^(?!\/__).*/],
      staticFileGlobsIgnorePatterns: [/\.map$/, /asset-manifest\.json$/],
    }),
    new Webpack.IgnorePlugin(/^\.\/locale$/, /moment$/),
    new HtmlCriticalWebpackPlugin({
      base: path.resolve(__dirname, '../build'),
      src: 'index.html',
      dest: 'index.html',
      inline: true,
      minify: true,
    })
  ],
  resolve: {
    alias: {
      'react-native': 'react-native-web',
    },
    extensions: ['.web.js', '.mjs', '.js', '.json', '.web.jsx', '.jsx'],
    modules: ['node_modules', paths.appNodeModules].concat(
      process.env.NODE_PATH.split(path.delimiter).filter(Boolean)
    ),
    plugins: [new ModuleScopePlugin(paths.appSrc, [paths.appPackageJson])],
  },
}
