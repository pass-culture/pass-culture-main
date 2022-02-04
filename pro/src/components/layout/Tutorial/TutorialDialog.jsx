import PropTypes from 'prop-types'
import React, { useCallback, useState } from 'react'

import { TUTO_DIALOG_LABEL_ID } from 'components/layout/Tutorial/_constants'
import DialogBox from 'new_components/DialogBox/DialogBox'

import * as pcapi from '../../../repository/pcapi/pcapi'

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

const TutorialDialog = ({ currentUser, setUserHasSeenTuto }) => {
  const [activeStepPosition, setActiveStepPosition] = useState(1)
  const [areTutoDisplayed, setAreTutoDisplayed] = useState(
    currentUser && !currentUser.hasSeenProTutorials
  )

  const closeTutoDialog = useCallback(() => {
    pcapi
      .setHasSeenTutos()
      .then(() => {
        setUserHasSeenTuto(currentUser)
      })
      .finally(() => setAreTutoDisplayed(false))
  }, [currentUser, setUserHasSeenTuto])

  const hasNextStep = getStep(activeStepPosition + 1) !== undefined
  const hasPreviousStep = getStep(activeStepPosition - 1) !== undefined
  const goToStep = useCallback(
    newStepPosition => () => setActiveStepPosition(newStepPosition),
    []
  )

  const activeStep = getStep(activeStepPosition)

  return areTutoDisplayed ? (
    <DialogBox
      extraClassNames="tutorial-box"
      hasCloseButton
      labelledBy={TUTO_DIALOG_LABEL_ID}
      onDismiss={closeTutoDialog}
    >
      <div className="tutorial" data-testid="tutorial-container">
        <activeStep.component titleId={TUTO_DIALOG_LABEL_ID} />

        <section className="tutorial-footer">
          <div className="nav-step-list-section">
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
          </div>

          <div className="nav-buttons-section">
            <button
              className="secondary-button"
              disabled={!hasPreviousStep}
              onClick={goToStep(activeStepPosition - 1)}
              type="button"
            >
              Précédent
            </button>
            {hasNextStep && (
              <button
                className="primary-button"
                onClick={goToStep(activeStepPosition + 1)}
                type="button"
              >
                Suivant
              </button>
            )}
            {!hasNextStep && (
              <button
                className="primary-button"
                onClick={closeTutoDialog}
                type="button"
              >
                Terminer
              </button>
            )}
          </div>
        </section>
      </div>
    </DialogBox>
  ) : null
}

TutorialDialog.defaultProps = {
  currentUser: null,
}

TutorialDialog.propTypes = {
  currentUser: PropTypes.shape(),
  setUserHasSeenTuto: PropTypes.func.isRequired,
}

export default TutorialDialog
