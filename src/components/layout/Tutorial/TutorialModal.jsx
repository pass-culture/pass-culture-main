import PropTypes from 'prop-types'
import React, { useEffect } from 'react'

import Tutorial from './Tutorial'

const TutorialModal = ({ closeTutorial, hasSeenTutorial, isFeatureActive, openTutorial }) => {
  useEffect(() => {
    if (isFeatureActive && !hasSeenTutorial) {
      openTutorial(<Tutorial onFinish={closeTutorial} />)
    }
  }, [closeTutorial, hasSeenTutorial, isFeatureActive, openTutorial])

  return null
}

TutorialModal.defaultProps = {}

TutorialModal.propTypes = {
  closeTutorial: PropTypes.func.isRequired,
  hasSeenTutorial: PropTypes.bool.isRequired,
  isFeatureActive: PropTypes.bool.isRequired,
  openTutorial: PropTypes.func.isRequired,
}

export default TutorialModal
