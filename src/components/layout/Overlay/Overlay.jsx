import PropTypes from 'prop-types'
import React from 'react'
import { Transition } from 'react-transition-group'

const duration = 500

const defaultStyle = {
  opacity: 0,
  transition: `opacity ${duration}ms ease`,
}

const transitionStyles = {
  entered: { opacity: 1 },
  entering: { opacity: 0 },
  exited: { display: 'none', visibility: 'none' },
}

const Overlay = ({ isVisible }) => (
  <Transition
    in={isVisible}
    timeout={!isVisible ? duration : 0}
  >
    {state => (
      <div
        className="is-overlay"
        id="overlay"
        style={{ ...defaultStyle, ...transitionStyles[state] }}
      />
    )}
  </Transition>
)

Overlay.propTypes = {
  isVisible: PropTypes.bool.isRequired,
}

export default Overlay
