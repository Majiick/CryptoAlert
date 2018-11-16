import _ from 'lodash';
import 'semantic-ui-css/semantic.min.css';
import { Button, Icon, Label } from 'semantic-ui-react'
import React from 'react';
import ReactDOM from 'react-dom';

function component() {
	let element = document.createElement('div');

	element.innerHTML = _.join(['xD', 'socketio'], ' ');
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

const ButtonExampleLabeledBasic = () => (
	  <div>
	    <Button as='div' labelPosition='right'>
	      <Button color='red'>
	        <Icon name='heart' />
	        Like
	      </Button>
	      <Label as='a' basic color='red' pointing='left'>
	        2,048
	      </Label>
	    </Button>
	    <Button as='div' labelPosition='right'>
	      <Button basic color='blue'>
	        <Icon name='fork' />
	        Fork
	      </Button>
	      <Label as='a' basic color='blue' pointing='left'>
	        2,048
	      </Label>
	    </Button>
	  </div>
)


class ShoppingList extends React.Component {
	  render() {
		      return ButtonExampleLabeledBasic(); 
		    }
}


ReactDOM.render(<ShoppingList name="Gabby" />, document.getElementById('root'));
//const element = <h1>Hello, world</h1>;
//ReactDOM.render(element, document.getElementById('root'));
//document.body.appendChild(ButtonExampleLabeledBasic());
//document.body.appendChild(component());
//document.body.appendChild(component());

