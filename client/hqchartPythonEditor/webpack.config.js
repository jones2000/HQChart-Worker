const path = require('path')
const resolve = require('path').resolve
const webpack = require('webpack')
const HtmlWebpackPlugin = require('html-webpack-plugin')
// const CopyPlugin = require('copy-webpack-plugin')
const FriendlyErrorsWebpackPlugin = require('friendly-errors-webpack-plugin')
const glob = require('glob')

const port = 8080;
// const port = 8010;

var os=require('os'),
    iptable='',
    ifaces=os.networkInterfaces();
for (var dev in ifaces) {
  ifaces[dev].forEach(function(details,alias){
    if (details.family=='IPv4' && details.address.match(/^192/)) {
      iptable=details.address;
    }
  });
}

const pages = glob.sync('./src/pages/*');
const pageEntry = pages.reduce((prev,curr)=>{
  prev[curr.slice(12)] = curr;
  return prev;
},{})
const pageHtmlWebpackPlugin = pages.map(item=>{
  var pageName=item.slice(12)
  return new HtmlWebpackPlugin({
    filename: pageName+'.html',
    template: 'src/index.html',
    chunks: [pageName,'vendor'],
    title: pageName
  })
})

module.exports = (options = {}) => ({
  entry: pageEntry,
  output: {
    path: resolve(__dirname, 'dist'),
    filename: options.dev ? '[name].js' : 'js/[name].js?[chunkhash:8]',//'[name].js' : '[name].js?[chunkhash]',
    chunkFilename: 'js/parts/[name].js?[chunkhash:8]',//'[id].js?[chunkhash]',
  },
  module: {
    rules: [{
        test: /\.vue$/,
        use: ['vue-loader']
      },
      {
        test: /\.js$/,
        use: ['babel-loader'],
        exclude: /node_modules/
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader', 'postcss-loader']
      },
      {
        test: /.less$/,
        loader: 'style-loader!css-loader!less-loader'
      },
      {
        test: /\.(png|jpg|jpeg|gif|eot|ttf|woff|woff2|svg|svgz)(\?.+)?$/,
        loader: 'file-loader',
        options: {
          name: "images/[name].[hash:8].[ext]",//'[name].[ext]?[hash]'
        }
      }
    ]
  },
  plugins: (function(){
    var plugins = [
      new webpack.DefinePlugin({
        'process.env': {
          ISDEV: options.dev
        }
      }),
      new webpack.optimize.CommonsChunkPlugin({
        names: ['vendor']
      }),
      // new CopyPlugin([
      //   { from: 'powerpaste/**/*', context: 'src' }
      // ])
    ]
    if(options.dev) {
      plugins.push(new FriendlyErrorsWebpackPlugin({
        compilationSuccessInfo: {
          messages: [
            `  Your App ${path.basename(__dirname)} running at:`,
            `  - Local:   http://localhost:${port}/`,
            `  - Network: http://${iptable}:${port}/`
          ]
        }
      }))
    }
    return plugins.concat(pageHtmlWebpackPlugin);
  })(),
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  devServer: {
    disableHostCheck: true,
    host: '0.0.0.0',
    port: port,
    quiet: true
  },
  stats: "normal",
  devtool: options.dev ? '#eval-source-map' : ''
})
