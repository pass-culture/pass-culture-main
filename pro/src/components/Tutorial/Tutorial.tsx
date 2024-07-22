import cn from 'classnames'
import React, { useCallback, useEffect, useState } from 'react'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'core/FirebaseEvents/constants'
import { useIsNewInterfaceActive } from 'hooks/useIsNewInterfaceActive'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import { TUTO_DIALOG_LABEL_ID } from './constants'
import { CreateOffer } from './Step/CreateOffer'
import { CreateVenue } from './Step/CreateVenue'
import { ManageBookings } from './Step/ManageBookings'
import { Welcome } from './Step/Welcome'
import styles from './Tutorial.module.scss'
import { Step } from './types'

const steps: Step[] = [
  {
    position: 1,
    component: Welcome,
    className: 'tutorial-content',
  },
  {
    position: 2,
    component: CreateVenue,
    className: 'two-columns-section',
  },
  {
    position: 3,
    component: CreateOffer,
    className: 'two-columns-section',
  },
  {
    position: 4,
    component: ManageBookings,
    className: 'tutorial-content',
  },
]

interface TutorialProps {
  onFinish: () => void
}

export const Tutorial = ({ onFinish }: TutorialProps): JSX.Element => {
  const { logEvent } = useAnalytics()
  const [activeStepPosition, setActiveStepPosition] = useState<number>(1)
  const isNewInterfaceActive = useIsNewInterfaceActive()

  const stepsToShow = isNewInterfaceActive
    ? steps.filter((step) => step.position !== 4)
    : steps

  const hasNextStep: boolean = activeStepPosition < stepsToShow.length
  const hasPreviousStep: boolean = activeStepPosition > 1
  const goToStep = useCallback(
    (newStepPosition: number) => () => setActiveStepPosition(newStepPosition),
    []
  )

  const activeStep =
    stepsToShow.find((step: Step) => step.position === activeStepPosition) ??
    stepsToShow[0]!

  useEffect(() => {
    logEvent(Events.TUTO_PAGE_VIEW, {
      page_number: activeStep.position.toString(),
    })
  }, [logEvent, activeStep])

  return (
    <div className={styles['tutorial']} data-testid="tutorial-container">
      <activeStep.component
        contentClassName={styles[activeStep.className] ?? ''}
        titleId={TUTO_DIALOG_LABEL_ID}
      />

      <section className={styles['tutorial-footer']}>
        <div className={styles['nav-step-list-section']}>
          {stepsToShow.map((step) => {
            const isActiveStep = activeStepPosition === step.position
            if (isNewInterfaceActive && step.position === 4) {
              return null
            }
            return (
              <button
                className={cn(styles['nav-step'], {
                  [styles['nav-step-active'] ?? '']: isActiveStep,
                  [styles['nav-step-done'] ?? '']:
                    activeStepPosition > step.position,
                })}
                data-testid="nav-dot"
                key={step.position}
                onClick={goToStep(step.position)}
                type="button"
                aria-current={isActiveStep ? 'page' : false}
                aria-label={`Étape du tutoriel ${step.position} sur ${stepsToShow.length}`}
              />
            )
          })}
        </div>

        <div className={styles['nav-buttons-section']}>
          <Button
            disabled={!hasPreviousStep}
            onClick={goToStep(activeStepPosition - 1)}
            variant={ButtonVariant.SECONDARY}
          >
            Précédent
          </Button>
          {hasNextStep && (
            <Button onClick={goToStep(activeStepPosition + 1)}>Suivant</Button>
          )}
          {!hasNextStep && <Button onClick={onFinish}>Terminer</Button>}
        </div>
      </section>
    </div>
  )
}
