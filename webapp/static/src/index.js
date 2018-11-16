import _ from 'lodash';
import 'semantic-ui-css/semantic.min.css';
import { Button, Icon, Label, Menu } from 'semantic-ui-react'
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

class AlertsButton extends React.Component {
	  render() {
		  return (
			  <div>
	    		  	<Button as='div' labelPosition='right'>
	                  		<Button color='red'>
	                  			<Icon name='exclamation triangle' />
	                  			Alerts
	                  		</Button>
	      				<Label as='a' basic color='red' pointing='left'>
	        				3
	     				</Label>
			  	</Button>
	  		  </div>
		  	);
	  }
}


class TopMenu extends React.Component {
    state = {activeItem: 'home'}
    handleItemClick = (e, { name }) => this.setState({ activeItem: name })

    render() {
        const { activeItem } = this.state;

        return (
          <Menu Inverted>
            <Menu.Item name='home' active={activeItem === 'home'} onClick={this.handleItemClick} />
            <Menu.Item name='alerts' active={activeItem === 'messages'} onClick={this.handleItemClick} />
            <Menu.Menu position='right'> <AlertsButton/> </Menu.Menu>

          </Menu>
        );
    }
}

ReactDOM.render(<TopMenu/>, document.getElementById('root'));
//const element = <h1>Hello, world</h1>;
//ReactDOM.render(element, document.getElementById('root'));
//document.body.appendChild(ButtonExampleLabeledBasic());
//document.body.appendChild(component());
//document.body.appendChild(component());

