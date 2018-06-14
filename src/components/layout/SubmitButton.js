import get from 'lodash.get'
import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { requestData } from '../../reducers/data'
import { randomHash } from '../../utils/random'

class SubmitButton extends Component {
  constructor() {
    super()
    this.state = {
      submitRequestId: null,
      submitRequestStatus: null
    }
  }

  onSubmitClick = event => {
    if (this.state.submitRequestId) return
    event.preventDefault()
    const {
      add,
      form,
      getBody,
      getNotification,
      getOptimistState,
      getSuccessState,
      history,
      isNotification,
      method,
      onClick,
      path,
      storeKey,
      redirect,
      redirectPathname,
      requestData,
    } = this.props
    const submitRequestId = randomHash()
    this.setState({
      submitRequestId,
    })
    requestData(method, path, {
      add,
      body: (getBody && getBody(form)) || form,
      getOptimistState,
      getSuccessState,
      key: storeKey,
      redirect,
      requestId: submitRequestId,
      isNotification,
      getNotification
    })
    onClick && onClick()
  }

  static getDerivedStateFromProps(nextProps, prevState) {
    if (prevState.submitRequestId) {
      const returnedQuery = nextProps.queries.find(
        q => q.id === prevState.submitRequestId
      )
      const submitRequestId = get(returnedQuery, 'status', '') === 'PENDING'
        ? returnedQuery.id
        : null
      return { submitRequestId }
    }
    return null
  }

  render() {
    const {
      className,
      form,
      getIsDisabled,
      submittingText,
      text,
    } = this.props
    const { submitRequestId } = this.state
    const isDisabled = getIsDisabled(form)
    return (
      <button
        className={classnames(className, {
          disabled: isDisabled,
        })}
        disabled={Boolean(submitRequestId) || isDisabled}
        onClick={this.onSubmitClick}
      >
        {submitRequestId ? submittingText : text}
      </button>
    )
  }
}

SubmitButton.defaultProps = {
  className: 'button',
  getBody: form => form,
  getIsDisabled: form => Object.keys(form).length === 0,
  method: 'POST',
  text: 'Soumettre',
  submittingText: 'Envoi ...',
}

SubmitButton.propTypes = {
  path: PropTypes.string.isRequired,
}

export default compose(
  withRouter,
  connect(
    ({ form, queries }) => ({
      form,
      queries,
    }),
    { requestData }
  )
)(SubmitButton)
