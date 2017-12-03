/* eslint-env node */
var path = require('path');
var webpack = require('webpack');

module.exports = function(env) {
    var nodeEnv = env === 'prod' ? 'production' : 'development';
    var isProd = nodeEnv === 'production';

    var plugins = [
        // new webpack.optimize.CommonsChunkPlugin({
        //     name: 'common'
        // }),
        new webpack.DefinePlugin({
            'process.env.NODE_ENV': JSON.stringify(nodeEnv)
        }),
        new webpack.LoaderOptionsPlugin({
            minimize: isProd === true,
            debug: isProd !== true
        })
    ];

    if (isProd) {
        plugins.push(
            new webpack.optimize.UglifyJsPlugin({
                beautify: false,
                sourceMap: true,
                mangle: {
                    screw_ie8: true,
                    keep_fnames: false
                },
                compress: {
                    warnings: false,
                    screw_ie8: true
                },
                comments: false
            })
        );
    }

    return {
        devtool: isProd ? 'source-map' : 'cheap-module-eval-source-map',
        entry: {
            app: ['whatwg-fetch', 'app.js']
        },

        plugins: plugins,

        module: {
            rules: [
                {
                    test: /\.js$/,
                    exclude: /(node_modules|bower_components)/,
                    use: {
                        loader: 'babel-loader',
                        options: {
                            presets: [
                                'react',
                                [
                                    'env',
                                    {
                                        targets: {
                                            browsers: ['last 2 version']
                                        }
                                    }
                                ]
                            ]
                        }
                    }
                },
                {
                    test: /\.scss$/,
                    use: [
                        {
                            loader: 'style-loader'
                        },
                        {
                            loader: 'css-loader'
                        },
                        {
                            loader: 'sass-loader',
                            options: {
                                // includePaths: ['node_modules/font-awesome/scss']
                            }
                        }
                    ]
                },
                {
                    test: /.(ttf|otf|eot|svg|woff(2)?)(\?[a-z0-9]+)?$/,
                    use: [
                        {
                            loader: 'file-loader',
                            options: {
                                name: '[name].[ext]',
                                outputPath: '../fonts/', // where the fonts will go
                                // publicPath: '../' // override the default path
                            }
                        }
                    ]
                }
            ]
        },

        resolve: {
            modules: [path.resolve('./web/src'), path.resolve('./web/sass'), 'node_modules']
        },

        output: {
            filename: '[name]' + '.js',
            path: path.resolve(__dirname, 'web', 'static', 'js')
        }
    };
};
