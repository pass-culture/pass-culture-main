import React from 'react'
import PropTypes from 'prop-types'

const SliderPoints = ({ currentStep, maxStep }) => {
  const points = () => {
    const pointsToDisplay = []

    for (let step = 0; step < maxStep; step++) {
      const isFilled = step === currentStep

      pointsToDisplay.push(
        <div
          className={`slider-point ${isFilled ? 'filled' : ''}`}
          key={step}
        />
      )
    }
    return pointsToDisplay
  }

  return points()
}

SliderPoints.propTypes = {
  currentStep: PropTypes.number.isRequired,
  maxStep: PropTypes.number.isRequired,
}

export default SliderPoints
