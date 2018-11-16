import _ from 'lodash';
import React from 'react';
import ReactDOM from 'react-dom';

function component() {
	let element = document.createElement('div');

	element.innerHTML = _.join(['lol', 'socketio'], ' ');
	return element;
}

const socket = io('http://209.97.181.63:443/');

socket.on('price_update', function (data) {
    console.log(data);
    //socket.emit('my other event', { my: 'data' });
});

socket.on('alert', function (data) {
    console.log('ALERT!!!');
    console.log(data);
});


class ShoppingList extends React.Component {
	  render() {
		      return (
			            <div className="shopping-list">
			              <h1>Shopping List for {this.props.name}</h1>
			              <ul>
			                <li>Instagram</li>
			                <li>WhatsApp</li>
			                <li>Oculus</li>
			              </ul>
			            </div>
			          );
		    }
}

ReactDOM.render(<ShoppingList name="Gabby" />, document.getElementById('root'));
//const element = <h1>Hello, world</h1>;
//ReactDOM.render(element, document.getElementById('root'));
//document.body.appendChild(element);
//document.body.appendChild(component());
//document.body.appendChild(component());

