import PropTypes from 'prop-types'
import React from 'react'

const TutorialStep = ({ children, isActive }) => (
  <div className={`tutorial-step ${isActive ? 'active' : ''}`}>
    {children}
  </div>
)

TutorialStep.defaultProps = {
  isActive: false,
}

TutorialStep.propTypes = {
  children: PropTypes.node.isRequired,
  isActive: PropTypes.bool,
}

export default TutorialStep
