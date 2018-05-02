import get from 'lodash.get'
import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import { requestData } from '../../reducers/data'
import { randomHash } from '../../utils/random'

class SubmitButton extends Component {
  constructor() {
    super()
    this.state = {
      submitRequestId: null,
    }
  }

  onSubmitClick = event => {
    if (this.state.submitRequestId) return
    event.preventDefault()
    const {
      add,
      form,
      getBody,
      getOptimistState,
      getSuccessState,
      method,
      onClick,
      path,
      storeKey,
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
      requestId: submitRequestId,
    })
    onClick && onClick()
  }

  static getDerivedStateFromProps(newProps, prevState) {
    if (prevState.submitRequestId) {
      const returnedQuery = newProps.queries.find(
        q => q.id === prevState.submitRequestId
      )
      return {
        submitRequestId:
          get(returnedQuery, 'status', '') === 'PENDING'
            ? returnedQuery.id
            : null,
      }
    }
    return null
  }

  render() {
    const { className, getIsDisabled, form, text, submittingText } = this.props
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

export default connect(
  ({ form, queries }) => ({
    form,
    queries,
  }),
  { requestData }
)(SubmitButton)
