const Autoprefixer = require('autoprefixer')
const CopyWebpackPlugin = require('copy-webpack-plugin')
const getClientEnvironment = require('./env')
const HtmlWebpackPlugin = require('html-webpack-plugin')
const InterpolateHtmlPlugin = require('react-dev-utils/InterpolateHtmlPlugin')
const ManifestPlugin = require('webpack-manifest-plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const Path = require('path')
const Paths = require('./paths')
const SWPrecacheWebpackPlugin = require('sw-precache-webpack-plugin')
const ModuleScopePlugin = require('react-dev-utils/ModuleScopePlugin')
const UglifyJsPlugin = require('uglifyjs-webpack-plugin')
const Webpack = require('webpack')

const publicPath = Paths.servedPath
const publicUrl = publicPath.slice(0, -1)
const env = getClientEnvironment(publicUrl)
const shouldUseSourceMap = process.env.GENERATE_SOURCEMAP !== 'false'

if (env.stringified['process.env'].NODE_ENV !== '"production"') {
  throw new Error('Production builds must have NODE_ENV=production.')
}

module.exports = {
  bail: true,
  devtool: shouldUseSourceMap ? 'source-map' : false,
  entry: [require.resolve('./polyfills'), Paths.appIndexJs],
  mode: 'production',
  optimization: {
    minimizer: [
      new UglifyJsPlugin({
        uglifyOptions: {
          compress: {
            comparisons: false,
          },
          output: {
            ascii_only: true,
            comments: false,
          },
          sourceMap: shouldUseSourceMap,
          warnings: false,
        },
      }),
    ],
    splitChunks: {
      cacheGroups: {
        styles: {
          name: 'styles',
          test: /\.css$/,
          chunks: 'all',
          enforce: true,
        },
      },
    },
  },
  output: {
    path: Paths.appBuild,
    filename: 'static/js/[name].[chunkhash:8].js',
    chunkFilename: 'static/js/[name].[chunkhash:8].chunk.js',
    publicPath: publicPath,
    devtoolModuleFilenameTemplate: info =>
      Path.relative(Paths.appSrc, info.absoluteResourcePath).replace(/\\/g, '/'),
  },
  performance: {
    maxAssetSize: 2500000,
    maxEntrypointSize: 3000000,
  },
  resolve: {
    modules: [Paths.appPath, 'node_modules', Paths.appNodeModules].concat(
      process.env.NODE_PATH.split(Path.delimiter)
        .filter(s => s !== '')
        .concat('src')
        .join(Path.delimiter)
    ),
    extensions: ['.web.js', '.mjs', '.js', '.json', '.web.jsx', '.jsx'],
    alias: {
      'react-native': 'react-native-web',
    },
    plugins: [new ModuleScopePlugin(Paths.appSrc, [Paths.appPackageJson])],
  },
  module: {
    strictExportPresence: true,
    rules: [
      {
        oneOf: [
          {
            test: [/\.bmp$/, /\.gif$/, /\.jpe?g$/, /\.png$/, /\.ttf$/],
            loader: 'url-loader',
            options: {
              limit: 10000,
              name: 'static/media/[name].[hash:8].[ext]',
            },
          },
          {
            test: /\.(js|jsx|mjs)$/,
            exclude: process.env.HAS_WORKERS && /index\.(.*)\.worker\.js$/ && /node_modules/,
            include: Paths.appSrc,
            loader: 'babel-loader',
            options: {
              compact: true,
            },
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
                    require('postcss-flexbugs-fixes'),
                    Autoprefixer({
                      overrideBrowserslist: ['>1%', 'last 4 versions', 'Firefox ESR', 'not ie < 9'],
                      flexbox: 'no-2009',
                    }),
                  ],
                },
              },
              {
                loader: 'sass-loader',
              },
            ],
          },
        ].concat([
          {
            loader: require.resolve('file-loader'),
            exclude: [/\.js$/, /\.html$/, /\.json$/],
            options: {
              name: 'static/media/[name].[hash:8].[ext]',
            },
          },
        ]),
      },
    ],
  },
  plugins: [
    new CopyWebpackPlugin(
      ['bmp', 'pdf', 'jpg', 'jpeg', 'png'].map(extension => ({
        from: Path.resolve(`${Paths.appPublic}/**/*.${extension}`),
        to: Path.resolve(`${Paths.appBuild}/**/*.${extension}`),
      }))
    ),
    new HtmlWebpackPlugin({
      inject: true,
      template: Paths.appHtml,
      minify: {
        collapseWhitespace: true,
        keepClosingSlash: true,
        minifyJS: true,
        minifyCSS: true,
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
      filename: '[name].css',
      chunkFileName: '[id].css',
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
        console.log(message)
      },
      minify: true,
      navigateFallback: publicUrl + '/index.html',
      navigateFallbackWhitelist: [/^(?!\/__).*/],
      staticFileGlobsIgnorePatterns: [/\.map$/, /asset-manifest\.json$/],
    }),
    new Webpack.IgnorePlugin(/^\.\/locale$/, /moment$/),
  ],
  node: {
    dgram: 'empty',
    fs: 'empty',
    net: 'empty',
    tls: 'empty',
    child_process: 'empty',
  },
}
