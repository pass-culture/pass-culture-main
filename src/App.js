import classnames from 'classnames'
import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

const App = ({ modalOpen, children }) => {
  return (
    <div className={classnames('app', { 'modal-open': modalOpen })}>
      {children}
    </div>
  )
}

export default compose(
  withRouter,
  connect(state => ({
    modalOpen: state.modal.isActive,
  }))
)(App)
