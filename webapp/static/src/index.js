import _ from 'lodash';

function component() {
	let element = document.createElement('div');

	element.innerHTML = _.join(['Bye', 'socketio'], ' ');
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

document.body.appendChild(component());
