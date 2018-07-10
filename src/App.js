import classnames from 'classnames'
import React, {Component} from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import Modal from './components/layout/Modal'
import { closeNotification } from './reducers/notification'


class App extends Component {

  componentWillMount() {
    this.unlisten = this.props.history.listen((location, action) => {
      this.props.closeNotification()
    })
  }

  componentWillUnmount() {
      this.unlisten()
  }

  render() {
    const {
      modalOpen,
      children,
    } = this.props
    return (
      <div className={classnames('app', {'modal-open': modalOpen})}>
        {children}
        <Modal />
      </div>
    )
  }
}

export default compose(
  withRouter,
  connect(store => ({
    modalOpen: store.modal.isActive,
  }), {
    closeNotification,
  })
)(App)
