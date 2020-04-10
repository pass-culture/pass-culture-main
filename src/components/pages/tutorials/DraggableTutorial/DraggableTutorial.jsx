import React from 'react'
import PropTypes from 'prop-types'
import Draggable from 'react-draggable'

const DraggableTutorial = ({ children, handleGoNext, handleGoPrevious, step }) => {
  const initialPosition = {
    x: 0,
    y: 0,
  }

  function calculateBounds() {
    return step === 0 ? { right: 0 } : {}
  }

  function handleStopDragging(event, data) {
    const tutorialHorizontalPosition = data.x
    const draggingDistanceToChangeTutorial = 150

    if (tutorialHorizontalPosition < -draggingDistanceToChangeTutorial) handleGoNext()

    if (tutorialHorizontalPosition > draggingDistanceToChangeTutorial) handleGoPrevious()
  }

  return (
    <Draggable
      axis="x"
      bounds={calculateBounds()}
      onStop={handleStopDragging}
      position={initialPosition}
    >
      <div className="tutorial">
        {children}
      </div>
    </Draggable>
  )
}

DraggableTutorial.propTypes = {
  children: PropTypes.node.isRequired,
  handleGoNext: PropTypes.func.isRequired,
  handleGoPrevious: PropTypes.func.isRequired,
  step: PropTypes.number.isRequired,
}

export default DraggableTutorial
