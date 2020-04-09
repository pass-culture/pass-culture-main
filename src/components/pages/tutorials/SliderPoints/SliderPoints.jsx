import React from 'react'
import PropTypes from 'prop-types'

const SliderPoints = ({ currentStep, elements }) => {
  return elements.map((step, index) => {
    const isFilled = index === currentStep
    return (<div
      className={`slider-point ${isFilled ? 'filled' : ''}`}
      key={step}
            />)
  })
}

SliderPoints.propTypes = {
  currentStep: PropTypes.number.isRequired,
  elements: PropTypes.arrayOf(PropTypes.func).isRequired,
}

export default SliderPoints
