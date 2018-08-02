import classnames from 'classnames'
import { Icon } from 'pass-culture-shared'
import React from 'react'
import { connect } from 'react-redux'

const Splash = ({ isActive, transitionTimeout }) => (
  <div
    className={classnames('splash', {
      'is-invisible': !isActive,
    })}
    style={{
      transition: `opacity ${transitionTimeout}ms, z-index 10ms ${transitionTimeout}ms`,
    }}
  >
    <Icon svg="logo-group" alt="Logo Pass Culture" />
  </div>
)

export default connect(state => ({
  isActive: state.splash.isActive,
  transitionTimeout: state.splash.transitionTimeout,
}))(Splash)
