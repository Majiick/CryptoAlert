import _ from 'lodash';
import 'semantic-ui-css/semantic.min.css';
import { Button, Icon, Label, Menu, List, Header, Container, Divider } from 'semantic-ui-react'
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
    constructor(props) {
        super(props);
      }

    render() {
      return (
          <div>
                <Button as='div' labelPosition='right'>
                    <Button color='red'>
                        <Icon name='exclamation triangle' />
                        Alerts
                    </Button>
                    <Label as='a' basic color='red' pointing='left'>
                        {this.props.number_alerts}
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
            <Menu.Item name='alerts' active={activeItem === 'alerts'} onClick={this.handleItemClick} />
            <Menu.Menu position='right'>
                <AlertsButton number_alerts={this.props.number_alerts}/>
            </Menu.Menu>

          </Menu>
        );
    }
}


class Alerts extends React.Component {
    constructor(props) {
        super(props);
        this.state = {alert_notification: [], subscribed_alerts: []};
        this.state.alert_notification.push(<List.Item>Test Alert Notification</List.Item>);
        this.state.subscribed_alerts.push(<List.Item>Test My Alert</List.Item>);
    }

    render() {
        return (
            <React.Fragment>
            <Container>
                <Header as='h2'>Alert Notifications</Header>
                <List>
                    {this.state.alert_notification}
                </List>
            </Container>

            <Divider />

            <Container>
                <Header as='h2'>My Alerts</Header>
                <List>
                    {this.state.subscribed_alerts}
                </List>
            </Container>
            </React.Fragment>
        );
    }
}

class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {number_alerts: 0}
    }

    render() {
        return (
            <React.Fragment>
                <TopMenu number_alerts={ this.state.number_alerts} />
                <Alerts />
            </React.Fragment>
        );
    }
}

ReactDOM.render(<App/>, document.getElementById('root'));
//const element = <h1>Hello, world</h1>;
//ReactDOM.render(element, document.getElementById('root'));
//document.body.appendChild(ButtonExampleLabeledBasic());
//document.body.appendChild(component());
//document.body.appendChild(component());

