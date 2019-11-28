import classnames from 'classnames'
import { compose } from 'redux'
import { connect } from 'react-redux'
import PropTypes from 'prop-types'
import React from 'react'
import { withRouter } from 'react-router'

const App = ({ modalOpen, children }) =>
  (
    <div className={classnames('app', { 'modal-open': modalOpen })}>
      {children}
    </div>
  )


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
