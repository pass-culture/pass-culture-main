import PropTypes from 'prop-types'
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

Splash.defaultProps = {
  transitionTimeout: '',
}

Splash.propTypes = {
  isActive: PropTypes.bool.isRequired,
  transitionTimeout: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
}

export default connect(state => ({
  isActive: state.splash.isActive,
  transitionTimeout: state.splash.transitionTimeout,
}))(Splash)
