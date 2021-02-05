import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import { DialogBox } from 'components/layout/DialogBox/DialogBox'
import { TUTO_DIALOG_LABEL_ID } from 'components/layout/Tutorial/_constants'

import CreateOffer from './Step/CreateOffer'
import CreateVenue from './Step/CreateVenue'
import ManageBookings from './Step/ManageBookings'
import Welcome from './Step/Welcome'

const steps = [
  {
    position: 1,
    component: Welcome,
  },
  {
    position: 2,
    component: CreateVenue,
  },
  {
    position: 3,
    component: CreateOffer,
  },
  {
    position: 4,
    component: ManageBookings,
  },
]
const getStep = position => steps.find(step => step.position === position)

const TutorialDialog = ({ hasSeenTutorial, isFeatureActive }) => {
  const [activeStepPosition, setActiveStepPosition] = useState(1)
  const [areTutoDisplayed, setAreTutoDisplayed] = useState(isFeatureActive && !hasSeenTutorial)

  const closeTutoDialog = useCallback(() => setAreTutoDisplayed(false), [])

  const hasNextStep = getStep(activeStepPosition + 1) !== undefined
  const hasPreviousStep = getStep(activeStepPosition - 1) !== undefined
  const goToStep = useCallback(newStepPosition => () => setActiveStepPosition(newStepPosition), [])

  const activeStep = getStep(activeStepPosition)

  return areTutoDisplayed ? (
    <DialogBox
      extraClassNames="tutorial-box"
      hasCloseButton
      labelledBy={TUTO_DIALOG_LABEL_ID}
      onDismiss={closeTutoDialog}
    >
      <div
        className="tutorial"
        data-testid="tutorial-container"
      >
        <section className="content-section">
          <activeStep.component titleId={TUTO_DIALOG_LABEL_ID} />
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
                data-testid="nav-dot"
                key={step.position}
                onClick={goToStep(step.position)}
                type="button"
              />
            )
          })}
        </section>

        <section className="nav-buttons-section">
          <button
            className="secondary-button"
            disabled={!hasPreviousStep}
            onClick={goToStep(activeStepPosition - 1)}
            type="button"
          >
            {'Précédent'}
          </button>
          {hasNextStep && (
            <button
              className="primary-button"
              onClick={goToStep(activeStepPosition + 1)}
              type="button"
            >
              {'Suivant'}
            </button>
          )}
          {!hasNextStep && (
            <button
              className="primary-button"
              onClick={closeTutoDialog}
              type="button"
            >
              {'Terminer'}
            </button>
          )}
        </section>
      </div>
    </DialogBox>
  ) : null
}

TutorialDialog.propTypes = {
  hasSeenTutorial: PropTypes.bool.isRequired,
  isFeatureActive: PropTypes.bool.isRequired,
}

export default TutorialDialog
