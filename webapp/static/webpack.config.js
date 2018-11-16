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
				test: /\.(png|woff|woff2|eot|ttf|svg)$/,
				loader: 'url-loader?limit=100000'
			  },
			  {
		                test: /\.s[a|c]ss$/,
		                loader: 'sass-loader!style-loader!css-loader'
		          },
		          {
		                test: /\.css$/,
		                loader: 'style-loader!css-loader'
		          }]
		},
};
