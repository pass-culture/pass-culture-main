import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

const App = ({ modalOpen, children }) => {
  return (<div className={classnames('app', { 'modal-open': modalOpen })}>
    {children}
  </div>)
}

function mapStateToProps(state) {
  return {
    modalOpen: state.modal.isActive,
  }
}

App.propTypes = {
  children: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  modalOpen: PropTypes.bool.isRequired,
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(App)
