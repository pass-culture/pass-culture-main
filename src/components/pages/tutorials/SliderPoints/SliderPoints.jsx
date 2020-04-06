import React from 'react'
import PropTypes from 'prop-types'

const SliderPoints = ({currentStep, elements}) => {
  return (
      elements.map((step, index)  => {
        let isFilled = index === currentStep
        return (
          <div
            className={`slider-point ${isFilled ? 'filled' : ''}`}
            key={step}
          />
        )
      })
  )
}

SliderPoints.propTypes = {
  currentStep: PropTypes.number.isRequired,
  elements: PropTypes.arrayOf(PropTypes.shape()).isRequired
}

export default SliderPoints
