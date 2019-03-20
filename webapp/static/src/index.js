import _ from 'lodash';
import 'semantic-ui-css/semantic.min.css';
import { Button, Icon, Label, Menu, List, Header, Container, Divider, Input, Segment, TransitionablePortal, Dropdown, Grid, Checkbox } from 'semantic-ui-react'
import React from 'react';
import ReactDOM from 'react-dom';
import { createStore } from 'redux';
import ReactTable from "react-table";
import 'react-table/react-table.css'
import './styles.css';
import { CSSTransitionGroup } from 'react-transition-group'

const reduxState = {
    jwt_token: '',
    updateMyAlerts: false,
    user_email: '',
    email_notification_value: false
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
      case "SETUSEREMAIL":
          state['user_email'] = action.email;
          return state;
      case "SETEMAILNOTIFICATIONVALUE":
          console.log('Set action.email_notification_value to ' + action.email_notification_value)
          state['email_notification_value'] = action.email_notification_value;
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
    constructor(props) {
        super(props);
        reduxStore.dispatch({type: 'TOPMENUSELECTION', selection: 'home'});
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
    }

    render() {
        let myMenu = []
        if ('POLONIEX' in this.props.latest_prices) {
            for (var key in this.props.latest_prices['POLONIEX']) {
                const price = this.props.latest_prices['POLONIEX'][key];
                myMenu.push(<div key={price}><Menu.Item>{key}: {price}</Menu.Item></div>)
            }
        } else {
            console.warn('No poloniex');
        }

        return (
            <CSSTransitionGroup
                transitionName="flash"
                transitionEnterTimeout={500}
                transitionLeaveTimeout={300}>

                <Menu Inverted> {myMenu} </Menu>
            </CSSTransitionGroup
        >
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
              data: JSON.stringify({alert: 'pricepoint', pair: this.state.pair, exchange: this.state.exchange, point: this.state.point, below_above: this.state.below_above, email_notification_value: reduxState.email_notification_value}),
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


class AddNotificationList extends React.Component {
    constructor(props) {
        super(props);
        this.state = {emailValue: ''};
    }

    render() {
        return(
          <React.Fragment>
              <Checkbox label='Email' onChange={(e, data) => reduxStore.dispatch({type: 'SETEMAILNOTIFICATIONVALUE', email_notification_value: data.checked})}/>
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
                    <Button basic color='violet'>
                      Volume Point
                    </Button>
                    <Button basic color='purple'>
                      Volume Percentage Change
                    </Button>
                  </div>


                  {this.state.activeAlert == 'price_point' ? (<CreateAlertPricePoint />) : null}
                  Notifications:
                  <AddNotificationList/>
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

class InterestingEvents extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        const data = [{
          time: '2:00 Feb 22',
          alert: 'Price spike',
          market: 'BTC_ETH',
          exchange: 'Poloniex',
          message: '5.8% ^'
        }]

        this.props.interesting_events.forEach((event) => {
           data.push({time: event['data']['event_time'], alert: event['data']['event_type'], market: event['data']['market'], exchange: event['data']['exchange'], message: event['data']['message']})
        });

        const columns = [{
            Header: 'Time',
            accessor: 'time' // String-based value accessors!
          }, {
            Header: 'Alert',
            accessor: 'alert'
          }, {
            Header: 'Market',
            accessor: 'market'
          }, {
            Header: 'Exchange',
            accessor: 'exchange'
          }, {
            Header: 'Message',
            accessor: 'message'
          }
        ]

        return <ReactTable
        data={data}
        columns={columns}
        />
    }
}

class App extends React.Component {
    constructor(props) {
        super(props);
        // this.state.updated_myalerts is to prevent infinite loop of changing redux state.
        // latest_prices is structured as latest_prices[exchange][pair] = 13.21
        this.state = {number_alerts: 0, alert_notification: [], subscribed_alerts: [], logged_in: false, updated_myalerts: true, latest_prices: {}, interesting_events: []}
        this.state.alert_notification.push(<List.Item>Test Alert Notification</List.Item>);
        this.state.subscribed_alerts.push(<List.Item>Test My Alert</List.Item>);

        var ws = new WebSocket("ws://46.101.82.15:8080/");
        ws.onmessage = (event) => {
            /*
            {"type": "price_update", "data": {"measurement": "latest_price", "exchange": "POLONIEX", "pair": "BTC_LTC", "price": 0.014792}}
             */

            var data = JSON.parse(event.data);
            console.log(data);
            if (data['type'] == 'price_update') {
                if (!(data['data']['exchange'] in this.state.latest_prices)) {
                    this.state.latest_prices[data['data']['exchange']] = {};
                    console.log('here');
                }
                this.state.latest_prices[data['data']['exchange']][data['data']['pair']] = data['data']['price']
                console.log(this.state.latest_prices)
                this.setState({});
            } else if (data['type'] == 'interesting_event') {
                console.log('Interesting event');
                this.state.interesting_events.push(data);
                this.setState({});
            } else if (data['type'] == 'alert') {
                console.log('ALERT!!!');
                this.state.alert_notification.push(<List.Item>{JSON.stringify(data)}</List.Item>);
                this.setState({});
            } else if (data['type'] == 'initial_interesting_events') {
                data['data'].forEach((event) => {
                    this.state.interesting_events.push({'data': event});
                });
                console.log(this.state.interesting_events);
                this.setState({});
            } else {
              console.warn('Dont know data type.');
            }

        }

        // const socket = io('http://46.101.82.15:8080/');
        // // const socket1 = io('http://46.101.82.15:8080/test');
        // // console.log("xDddddddddddd")
        // // socket1.on('connect', function() {
        // //         console.log("i'm conected")
        // //     });
        //
        // socket.on('connection_established', (data) => {
        //     console.log('Connection established ' + data);
        //     document.title = "E" + document.title;
        // });
        //
        // socket.on('price_update', (data) => {
        //     console.log("Price update")
        //     console.log(data);
        //     console.log("NOT ADDING TO PRICE AUPDATRES");
        //     // this.state.price_updates.push(data);
        //     console.log(this.state.price_updates);
        //     this.setState({});
        //     //socket.emit('my other event', { my: 'data' });
        // });
        //
        // console.log('Registering interesting event')
        // socket.on('interesting_event', (data) => {
        //     console.log("Interesting event")
        //     console.log(data);
        //     this.state.interesting_events.push(data);
        //     this.setState({});
        // });
        //
        // // Only rerenders on setState not just this.state.something = whatever
        // socket.on('alert', (data) => {
        //     if(this.state.logged_in) {
        //         console.log('ALERT!!!');
        //         this.state.alert_notification.push(<List.Item>{JSON.stringify(data)}</List.Item>);
        //         this.setState({});
        //         console.log(data);
        //         console.log(this.state.subscribed_alerts);
        //     }
        // });

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
            return (
                <React.Fragment>
                    <TopMenu number_alerts={ this.state.number_alerts} />
                    <TopLatestPrices latest_prices={state_.latest_prices}/>
                    {reduxState.topMenuSelection == 'alerts' ? (
                                <Alerts subscribed_alerts={state_.subscribed_alerts} alert_notification={state_.alert_notification}/>
                        ) : null
                    }
                    {reduxState.topMenuSelection == 'home' ? (
                                <InterestingEvents interesting_events={state_.interesting_events}/>
                        ) : null
                    }
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

