import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { requestData, reinitializeData } from 'redux-saga-data'

import { closeModal } from 'store/reducers/modal'

class SignoutButton extends Component {
  handleFail = () => {
    const { handleFail, handleFailRedirect, history } = this.props
    if (handleFail) {
      handleFail(this.props)
      return
    }

    const redirect = handleFailRedirect && handleFailRedirect()
    if (redirect) {
      history.push(redirect)
    }
  }

  handleSuccess = () => {
    const {
      dispatch,
      handleSuccess,
      handleSuccessRedirect,
      history,
      noreinitializeData,
    } = this.props
    if (handleSuccess) {
      handleSuccess(this.props)
      return
    }

    if (!noreinitializeData) {
      dispatch(reinitializeData())
    }

    const redirect = handleSuccessRedirect && handleSuccessRedirect()
    if (redirect) {
      history.push(redirect)
    }
  }

  onSignoutClick = () => {
    const { dispatch } = this.props
    dispatch(
      requestData({
        apiPath: '/users/signout',
        handleFail: this.handleFail,
        handleSuccess: this.handleSuccess,
        name: 'signout',
      })
    )
    dispatch(closeModal())
  }

  render() {
    const { children, className, Tag } = this.props
    return (
      <Tag
        className={className}
        onClick={this.onSignoutClick}
      >
        {children}
      </Tag>
    )
  }
}

SignoutButton.defaultProps = {
  Tag: 'button',
  children: null,
  className: null,
  handleFail: null,
  handleFailRedirect: null,
  handleSuccess: null,
  handleSuccessRedirect: null,
  noreinitializeData: null,
}

SignoutButton.propTypes = {
  Tag: PropTypes.string,
  children: PropTypes.node,
  className: PropTypes.string,
  dispatch: PropTypes.func.isRequired,
  handleFail: PropTypes.func,
  handleFailRedirect: PropTypes.func,
  handleSuccess: PropTypes.func,
  handleSuccessRedirect: PropTypes.func,
  history: PropTypes.shape().isRequired,
  noreinitializeData: PropTypes.bool,
}

export default compose(withRouter, connect())(SignoutButton)
