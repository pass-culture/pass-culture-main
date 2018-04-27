import classnames from 'classnames'
import React from 'react'
import { connect } from 'react-redux'

import Icon from './Icon'

const Splash = ({ isActive, transitionTimeout }) => {
  return (
    <div
      className={classnames(
        'splash',
        {
          'is-invisible': !isActive,
        }
      )}
      style={{
        transition: `opacity ${transitionTimeout}ms, z-index 10ms ${transitionTimeout}ms`,
      }}
    >
      <Icon svg="logo-group" />
    </div>
  )
}

export default connect(state => ({
  isActive: state.splash.isActive,
  transitionTimeout: state.splash.transitionTimeout,
}))(Splash)
