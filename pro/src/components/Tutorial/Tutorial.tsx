import cn from 'classnames'
import React, { useCallback, useEffect, useState } from 'react'

import {
  CreateOffer,
  CreateVenue,
  ManageBookings,
  Welcome,
} from 'components/Tutorial/Step'
import { Events } from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { TUTO_DIALOG_LABEL_ID } from './constants'
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
const getStep = (position: number): Step | undefined =>
  steps.find((step: Step) => step.position === position)

interface TutorialProps {
  onFinish: () => void
}

const Tutorial = ({ onFinish }: TutorialProps): JSX.Element => {
  const { logEvent } = useAnalytics()
  const [activeStepPosition, setActiveStepPosition] = useState<number>(1)
  const hasNextStep: boolean = getStep(activeStepPosition + 1) !== undefined
  const hasPreviousStep: boolean = getStep(activeStepPosition - 1) !== undefined
  const goToStep = useCallback(
    (newStepPosition: number) => () => setActiveStepPosition(newStepPosition),
    []
  )
  const activeStep = getStep(activeStepPosition) as Step

  useEffect(() => {
    logEvent?.(Events.TUTO_PAGE_VIEW, {
      page_number: activeStep.position.toString(),
    })
  }, [activeStep])

  return (
    <div className={styles['tutorial']} data-testid="tutorial-container">
      <activeStep.component
        contentClassName={styles[activeStep.className]}
        titleId={TUTO_DIALOG_LABEL_ID}
      />

      <section className={styles['tutorial-footer']}>
        <div className={styles['nav-step-list-section']}>
          {steps.map(step => {
            const navStepClasses = [styles['nav-step']]
            if (activeStepPosition === step.position) {
              navStepClasses.push(styles['nav-step-active'])
            } else if (activeStepPosition > step.position) {
              navStepClasses.push(styles['nav-step-done'])
            }

            return (
              <button
                className={cn(navStepClasses)}
                data-testid="nav-dot"
                key={step.position}
                onClick={goToStep(step.position)}
                type="button"
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

export default Tutorial
