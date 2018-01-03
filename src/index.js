import React from 'react';
import ReactDOM from 'react-dom';
import './styles/index.scss';
import registerServiceWorker from './utils/registerServiceWorker';
import Root from './Root';

ReactDOM.render(<Root />, document.getElementById('root'));
registerServiceWorker();
