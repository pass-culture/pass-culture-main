import classnames from 'classnames'
import React, { Component } from 'react'

import Icon from '../components/Icon'

const withSplash = (config = {}) => WrappedComponent => {
  const { children, triggerRemoveSplashTimeout } = config
  const removeSplashTimeout = config.removeSplashTimeout || 2000

  class _withSplash extends Component {
    constructor() {
      super()
      this.state = { hasSplash: true }
    }

    handleRemoveSplash = localRemoveSplashTimeout => {
      if (!this.removeSplashTimeout) {
        this.removeSplashTimeout = setTimeout(
          () => this.setState({ hasSplash: false }),
          localRemoveSplashTimeout || removeSplashTimeout
        )
      }
    }

    componentWillMount() {
      if (triggerRemoveSplashTimeout) {
        this.triggerRemoveSplashTimeout = setTimeout(
          () => this.handleRemoveSplash(),
          triggerRemoveSplashTimeout
        )
      }
    }

    componentWillUnmount() {
      this.triggerRemoveSplashTimeout &&
        clearTimeout(this.triggerRemoveSplashTimeout)
      this.removeSplashTimeout && clearTimeout(this.removeSplashTimeout)
    }

    render() {
      return [
        <div
          className={classnames('splash', {
            hidden: !this.state.hasSplash,
          })}
          key={0}
        >
          {children}
        </div>,
        <WrappedComponent
          key={1}
          {...this.props}
          handleRemoveSplash={this.handleRemoveSplash}
        />,
      ]
    }
  }
  return _withSplash
}

export default withSplash
