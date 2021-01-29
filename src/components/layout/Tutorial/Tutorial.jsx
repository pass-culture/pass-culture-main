import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import CreateOffer from './Step/CreateOffer'
import CreateVenue from './Step/CreateVenue'
import ManageBookings from './Step/ManageBookings'
import Welcome from './Step/Welcome'
import TutorialStep from './TutorialStep'

const steps = [
  {
    position: 1,
    component: Welcome,
  },
  {
    position: 2,
    component: CreateOffer,
  },
  {
    position: 3,
    component: CreateVenue,
  },
  {
    position: 4,
    component: ManageBookings,
  },
]

const Tutorial = ({ onFinish }) => {
  const [activeStepPosition, setActiveStepPosition] = useState(1)
  const getStep = useCallback(position => steps.find(step => step.position === position), [])

  const hasNextStep = getStep(activeStepPosition + 1) !== undefined
  const hasPreviousStep = getStep(activeStepPosition - 1) !== undefined

  const goToStep = useCallback(
    newStepPosition => {
      const hasStep = getStep(newStepPosition) !== undefined
      if (hasStep) {
        setActiveStepPosition(newStepPosition)
      }
    },
    [getStep, setActiveStepPosition]
  )
  const stepClick = useCallback(
    e => {
      goToStep(parseInt(e.target.dataset.step))
    },
    [goToStep]
  )

  return (
    <div
      className="tutorial"
      data-testid="tutorial-container"
    >
      <section className="content-section">
        {steps.map(step => (
          <TutorialStep
            isActive={activeStepPosition === step.position}
            key={`tutorial-step-${step.position}`}
          >
            <step.component />
          </TutorialStep>
        ))}
      </section>

      <section className="nav-step-list-section">
        {steps.map(step => {
          let navStepClasses = ['nav-step']
          if (activeStepPosition === step.position) {
            navStepClasses.push('nav-step-active')
          } else if (activeStepPosition > step.position) {
            navStepClasses.push('nav-step-done')
          }

          return (
            <button
              className={navStepClasses.join(' ')}
              data-step={step.position}
              data-testid="nav-dotte"
              key={step.position}
              onClick={stepClick}
              type="button"
            />
          )
        })}
      </section>

      <section className="nav-buttons-section">
        <button
          className="secondary-button"
          data-step={activeStepPosition - 1}
          disabled={!hasPreviousStep}
          onClick={stepClick}
          type="button"
        >
          {'Précédent'}
        </button>
        {hasNextStep && (
          <button
            className="primary-button"
            data-step={activeStepPosition + 1}
            onClick={stepClick}
            type="button"
          >
            {'Suivant'}
          </button>
        )}
        {!hasNextStep && onFinish && (
          <button
            className="primary-button"
            onClick={onFinish}
            type="button"
          >
            {'Términer'}
          </button>
        )}
      </section>
    </div>
  )
}

Tutorial.defaultProps = {
  onFinish: false,
}

Tutorial.propTypes = {
  onFinish: PropTypes.oneOfType([PropTypes.func, PropTypes.oneOf([false])]),
}

export default Tutorial
