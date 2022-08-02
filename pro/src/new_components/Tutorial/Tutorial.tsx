import cn from 'classnames'
import React, { useCallback, useEffect, useState } from 'react'

import useAnalytics from 'components/hooks/useAnalytics'
import { Events } from 'core/FirebaseEvents/constants'
import {
  CreateOffer,
  CreateVenue,
  ManageBookings,
  Welcome,
} from 'new_components/Tutorial/Step'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { TUTO_DIALOG_LABEL_ID } from './constants'
import styles from './Tutorial.module.scss'
import { IStep } from './types'

const steps: IStep[] = [
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
const getStep = (position: number): IStep | undefined =>
  steps.find((step: IStep) => step.position === position)

interface ITutorialProps {
  onFinish: () => void
}

const Tutorial = ({ onFinish }: ITutorialProps): JSX.Element => {
  const { logEvent } = useAnalytics()
  const [activeStepPosition, setActiveStepPosition] = useState<number>(1)
  const hasNextStep: boolean = getStep(activeStepPosition + 1) !== undefined
  const hasPreviousStep: boolean = getStep(activeStepPosition - 1) !== undefined
  const goToStep = useCallback(
    (newStepPosition: number) => () => setActiveStepPosition(newStepPosition),
    []
  )
  const activeStep = getStep(activeStepPosition) as IStep

  useEffect(() => {
    logEvent?.(Events.TUTO_PAGE_VIEW, {
      page_number: activeStep.position.toString(),
    })
  }, [activeStep])

  return (
    <div className={styles['tutorial']} data-testid="tutorial-container">
      <activeStep.component
        contentClassName={styles['tutorial-content']}
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
