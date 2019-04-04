const path = require('path');

module.exports = {
	entry: './src/index.js',
	output: {
		filename: 'bundle.js',
		path: path.resolve(__dirname, 'dist')
	},
	module: {
		rules: [{
				test: /\.js$/,
				exclude: /node_modules/,
				use: [{
					loader: "babel-loader"
				}]
			  }, {
				test: /\.(png|woff|woff2|eot|ttf|svg)$/,  // For importing css with semantics ui
				loader: 'url-loader?limit=100000'
			  },
			  {
		                test: /\.s[a|c]ss$/,  // For importing css with semantics ui
		                loader: 'sass-loader!style-loader!css-loader'
		          },
		          {
		                test: /\.css$/,  // For importing css with semantics ui
		                loader: 'style-loader!css-loader'
		          }]
		},
		optimization: {
					// We no not want to minimize our code.
					minimize: false

		},
};
