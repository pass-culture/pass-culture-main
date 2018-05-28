import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import Icon from '../layout/Icon'

const withBackButton = (
  connectFn = () => ({}),
  btnClass = ''
) => WrappedComponent => {
  class _withBackButton extends Component {
    static defaultProps = {
      isActive: true,
    }

    render() {
      const { isActive, history, ...otherProps } = this.props
      if (isActive) {
        return (
          <div>
            <button
              className={`button back ${btnClass}`}
              onClick={history.goBack}
            >
              <Icon svg="ico-back-simple-w" alt="Retour" />
            </button>
            <WrappedComponent {...otherProps} />
          </div>
        )
      }
      return <WrappedComponent {...otherProps} />
    }
  }
  return compose(
    withRouter,
    connect(
      state => {
        const { isActive } = connectFn(state)
        return { isActive }
      },
      () => ({})
    )
  )(_withBackButton)
}

export default withBackButton
