import _ from 'lodash';
import 'semantic-ui-css/semantic.min.css';
import { Button, Icon, Label, Menu, List, Header, Container, Divider, Input, Segment, TransitionablePortal, Dropdown, Grid } from 'semantic-ui-react'
import React from 'react';
import ReactDOM from 'react-dom';
import { createStore } from 'redux'

const reduxState = {
    jwt_token: '',
    updateMyAlerts: false
}

function reduxReducer(state, action) {
  if (typeof state === 'undefined') {
    return reduxState;
  }

  switch (action.type) {
      case "JWTTOKEN":
          state['jwt_token'] = action.token;
          console.log('jwt token updated');
          return state;
      case "TOPMENUSELECTION":
          state['topMenuSelection'] = action.selection;
	      console.log('top menu selection dispatched selection: ' + action.selection);
	  return state;
      case "UPDATEMYALERTS":
          state['updateMyAlerts'] = action.update;
          console.log('Update my alerts updated to: ' + action.update);
	      return state;
      default:
          console.warn('Default redux action, state not changed, action.');
          console.warn(action);
          return state;
  }

  return state;
}

const reduxStore = createStore(reduxReducer);

function component() {
	let element = document.createElement('div');

	element.innerHTML = _.join(['xD', 'socketio'], ' ');
	return element;
}

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


class LoginButtonAndForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            login: '',
            password: '',
	    open: false
        };
    }

    render() {
	const {open} = this.state;
      return (
	<React.Fragment>
	      <Button
	         content={open ? 'Login' : 'Login'}
	         negative={open}
	         positive={!open}
	         onClick={() => this.setState({open: !this.state.open})}
	      />

	  <TransitionablePortal onClose={() => this.setState({open: false})} open={open}>
          <Segment style={{left: '40%', position: 'fixed', top: '50%', zIndex: 1000}}>
              <Input focus placeholder='User' onChange={(e) => this.state.login = e.target.value} />
              <Input focus type='password' placeholder='Password' onChange={(e) => this.state.password = e.target.value} />
              <Button onClick={(e) => this.handleLoginClick(e)}>Login</Button>
          </Segment>
	  </TransitionablePortal>
	</React.Fragment>
        );
    }

    handleLoginClick() {
        console.log(this.state.login);
        console.log(this.state.password);

        // Flask Login
        $.ajax({
              type: "POST",
              contentType: "application/json; charset=utf-8",
              url: "/login",
              data: JSON.stringify({username: this.state.login, password: this.state.password}),
              success: function (data) {
                      alert(data);
                    }
        });

        // JWT Login
        $.ajax({
              type: "POST",
              contentType: "application/json; charset=utf-8",
              url: "/auth",
              data: JSON.stringify({username: this.state.login, password: this.state.password}),
              dataType: "json",
              success: function (data) {
                      reduxStore.dispatch({type: 'JWTTOKEN', token: data['access_token']});
                    }
        });
    }
}

class TopMenu extends React.Component {
    state = {activeItem: 'home'}
    handleItemClick = (e, { name }) => {
	    this.setState({ activeItem: name });
	    reduxStore.dispatch({type: 'TOPMENUSELECTION', selection: name});
    }

    render() {
        const { activeItem } = this.state;

        return (
          <Menu Inverted>
            <Menu.Item name='home' active={activeItem === 'home'} onClick={this.handleItemClick} />
            <Menu.Item name='alerts' active={activeItem === 'alerts'} onClick={this.handleItemClick} />
            <Menu.Menu position='right'>
                <AlertsButton number_alerts={this.props.number_alerts}/>
                <LoginButtonAndForm/>
            </Menu.Menu>

          </Menu>
        );
    }
}


class TopLatestPrices extends React.Component {
    constructor(props) {
        super(props);

        this.state = {prices: {}}
    }

    render() {
        console.log('price_updates ' + this.props.price_updates.toString());
        this.props.price_updates.forEach((update) => {
           this.state.prices[update['data']['pair']] = update['data']['price'];
        });

        let myMenu = []
        for (var key in this.state.prices) {
            myMenu.push(<Menu.Item>{key} + ': ' + {this.state.prices[key]}</Menu.Item>)
        }

        return (
          <Menu Inverted> {myMenu} </Menu>
        );
    }
}


class CreateAlertPricePoint extends React.Component {
    constructor(props) {
        super(props);
        this.state = {point: 0, exchange: '', pair: '', below_above: ''};
    }

    createAlertButtonClicked() {
        if (reduxState.jwt_token == '') {
            console.warn('JWT Token not set for create alert');
            return;
        }

	    $.ajax({
              type: "POST",
              contentType: "application/json; charset=utf-8",
              headers: {"Authorization": "JWT " + reduxState.jwt_token},
              url: "/createalert",
              data: JSON.stringify({alert: 'pricepoint', pair: this.state.pair, exchange: this.state.exchange, point: this.state.point, below_above: this.state.below_above}),
              dataType: "json",
              success: (data) => {
                      console.log("Server said this on createalert: ");
                      console.log(data);
                      reduxStore.dispatch({type: 'UPDATEMYALERTS', update: true});
                    }
        });


    }

    render() {
        const exchangeOptions = [
          { key: 'poloniex', text: 'Poloniex', value: 'poloniex' },
          { key: 'bittrex', text: 'Bittrex', value: 'bittrex' },
          { key: 'kraken', text: 'Kraken', value: 'kraken' }
        ];

        const pairOptions = [
          { key: 'btcusd', text: 'BTCUSD', value: 'btcusd' },
          { key: 'btceth', text: 'BTCETH', value: 'btceth' },
          { key: '*', text: 'All', value: '*' }
        ];

        const belowAboveOptions = [
          { key: 'above', text: 'Above', value: 'above' },
          { key: 'below', text: 'Below', value: 'below' }
        ];

        return(
          <React.Fragment>
              <Input focus placeholder='Price Point' onChange={(e) => this.setState({point: e.target.value})} />
              <Dropdown placeholder='Pair' fluid multiple selection options={pairOptions} onChange={(e, { value }) => this.setState({pair: value})} />
              <Dropdown placeholder='Exchange' fluid multiple selection options={exchangeOptions} onChange={(e, { value }) => this.setState({exchange: value})} />
              <Dropdown placeholder='Below/Above' fluid selection options={belowAboveOptions} onChange={(e, { value }) => this.setState({below_above: value})} />
              <Button onClick={(e) => this.createAlertButtonClicked(e)}>Create Alert</Button>
          </React.Fragment>
        );
    }
}


class CreateAlert extends React.Component {
    constructor(props) {
        super(props);
        this.state = {activeAlert: 'none'};
    }

    render() {
        return(
             <Segment style={{left: '40%', position: 'fixed', top: '50%', zIndex: 1000}}>
                  <h1>Create Alert</h1>
                  <div>
                    <Button basic onClick={() => this.setState({activeAlert: 'price_point'})}>
                      Price Point
                    </Button>
                    <Button basic color='red' onClick={() => this.setState({activeAlert: 'price_percentage_change'})}>
                      Price Percentage Change
                    </Button>
                    <Button basic color='orange' onClick={() => this.setState({activeAlert: 'price_divergence'})}>
                      Price Divergence
                    </Button>
                    <Button basic color='yellow' onClick={() => this.setState({activeAlert: 'profitloss'})}>
                      Profit/Loss
                    </Button>
                    <Button basic color='violet'>
                      Volume Point
                    </Button>
                    <Button basic color='purple'>
                      Volume Percentage Change
                    </Button>
                    <Button basic color='pink'>
                      New Coin
                    </Button>
                  </div>

        {this.state.activeAlert == 'price_point' ? (<CreateAlertPricePoint />) : null}
              </Segment>
        );
    }
}


class Alerts extends React.Component {
    constructor(props) {
        super(props);
        this.state = {createalertopen: false}
    }

    createAlertButtonClicked() {
	    console.log('Create alert button clicked');
    }

    render() {
        return (
            <React.Fragment>
                <Button
                     content={this.state.createalertopen ? 'Create Alert' : 'Create Alert'}
                     negative={this.state.createalertopen}
                     positive={!this.state.createalertopen}
                     onClick={() => this.setState({createalertopen: !this.state.createalertopen})}
                  />

                <TransitionablePortal onClose={() => this.setState({createalertopen: false})} open={this.state.createalertopen}>
                  <CreateAlert />
                </TransitionablePortal>

            <Container>
                <Header as='h2'>Alert Notifications</Header>
                <List>
                    {this.props.alert_notification}
                </List>
            </Container>

            <Divider />

            <Container>
                <Header as='h2'>My Alerts</Header>
                <List>
                    {this.props.subscribed_alerts}
                </List>
            </Container>
            </React.Fragment>
        );
    }
}

class App extends React.Component {
    constructor(props) {
        super(props);
        console.log("wtf")
        // this.state.updated_myalerts is to prevent infinite loop of changing redux state.
        this.state = {number_alerts: 0, alert_notification: [], subscribed_alerts: [], logged_in: false, updated_myalerts: true, price_updates: []}
        this.state.alert_notification.push(<List.Item>Test Alert Notification</List.Item>);
        this.state.subscribed_alerts.push(<List.Item>Test My Alert</List.Item>);

        console.log("Hello");

        const socket = io('http://46.101.82.15:443/');

        socket.on('price_update', (data) => {
            console.log("Price update")
            console.log(data);
            this.state.price_updates.push(data);
            console.log(this.state.price_updates);
            this.setState({});
            //socket.emit('my other event', { my: 'data' });
        });

        // Only rerenders on setState not just this.state.something = whatever
        socket.on('alert', (data) => {
            if(this.state.logged_in) {
                console.log('ALERT!!!');
                this.state.alert_notification.push(<List.Item>{JSON.stringify(data)}</List.Item>);
                this.setState({});
                console.log(data);
                console.log(this.state.subscribed_alerts);
            }
        });

        let reduxChangedState = () => {
            if (reduxState.jwt_token) {
                if (!this.state.logged_in) {  // On first login
                    console.log("First login updating my alerts " + this.state.logged_in);
                    this.updateMyAlerts();
                }

                this.state.logged_in = true;
                if (!this.state.updated_myalerts) {
                    reduxStore.dispatch({type: 'UPDATEMYALERTS', update: false});
                    this.state.updated_myalerts = true;
                    //this.state.updated_myalerts is to prevent infinite loop of changing redux state.
                    setTimeout(() => this.state.updated_myalerts = false, 500);  // Set
                }
            }

            if (reduxState.updateMyAlerts == true) {
                this.updateMyAlerts();
                if (!this.state.updated_myalerts) {
                    reduxStore.dispatch({type: 'UPDATEMYALERTS', update: false});
                    this.state.updated_myalerts = true;
                    //this.state.updated_myalerts is to prevent infinite loop of changing redux state.
                    setTimeout(() => this.state.updated_myalerts = false, 500);
                }
            }

            console.log('Update app state');
            this.setState({}); // Update state for topmenu redux update
        }

        reduxStore.subscribe(reduxChangedState);
    }

    updateMyAlerts() {
        // Update my alerts
        if (!reduxState.jwt_token) {
            console.warn('No JWT token set, cannot update my alerts.');
            return;
        }

        console.log("Updating alerts");

        $.ajax({
              type: "GET",
              headers: {"Authorization": "JWT " + reduxState.jwt_token, contentType: "application/json; charset=utf-8"},
              url: "/getsubscribedalerts",
              dataType: "json",
              success: (data) => {
                      this.state.subscribed_alerts = [];
                      this.state.subscribed_alerts.push(<List.Item>{JSON.stringify(data)}</List.Item>);
                      this.setState({});
                    }
        });
    }

    render() {
        const state_ = this.state;
        console.log(reduxState.topMenuSelection);
            return (
                <React.Fragment>
                    <TopMenu number_alerts={ this.state.number_alerts} />
                    <TopLatestPrices price_updates={state_.price_updates}/>
                    {reduxState.topMenuSelection == 'alerts' ? (
                                <Alerts subscribed_alerts={state_.subscribed_alerts} alert_notification={state_.alert_notification}/>
                        ) : null
                    }
                </React.Fragment>
            );
    }
}

console.log("Hello");

ReactDOM.render(<App/>, document.getElementById('root'));
//const element = <h1>Hello, world</h1>;
//ReactDOM.render(element, document.getElementById('root'));
//document.body.appendChild(ButtonExampleLabeledBasic());
//document.body.appendChild(component());
//document.body.appendChild(component());

