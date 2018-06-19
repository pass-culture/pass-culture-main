import React, {Component} from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { closeNotification } from './reducers/notification'

import Modal from './components/layout/Modal'
import Splash from './components/layout/Splash'


class App extends Component {

  componentWillMount() {
    this.unlisten = this.props.history.listen((location, action) => {
      console.log(location, action)
      this.props.closeNotification()
    });
  }
  componentWillUnmount() {
      this.unlisten();
  }

  render() {
    return (
      <div className="app">
        {this.props.children}
        <Modal />
        <Splash />
      </div>
    )
  }
}

export default compose(
  withRouter,
  connect(null, {
    closeNotification,
  })
)(App)

