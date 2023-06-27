import cn from 'classnames'
import React from 'react'

import type { Step } from 'components/Breadcrumb'
import StepContent from 'components/Stepper/StepContent'
import { findLastIndex } from 'utils/findLastIndex'

import styles from './Stepper.module.scss'

export interface StepperProps {
  activeStep: string
  steps: Step[]
  className?: string
}

const Stepper = ({
  activeStep,
  steps,
  className,
}: StepperProps): JSX.Element => {
  const lastStepIndex = steps.length - 1
  const lastLineToActivate = findLastIndex(steps, (step: Step) => !!step.url)

  return (
    <>
      <ul className={cn(styles[`stepper`], className)} data-testid="stepper">
        {steps.map((step, stepIndex) => {
          const isActive = activeStep === step.id
          const isLastStep = lastStepIndex === stepIndex
          const isSelectionnable = !!step.url

          return (
            <li
              className={cn(
                styles['step-container'],
                isSelectionnable && styles['selectionnable'],
                isActive && styles['active']
              )}
              key={`step-${step.id}`}
              data-testid={`step-${step.id}`}
            >
              <StepContent step={step} stepIndex={stepIndex} />
              {!isLastStep && (
                <div
                  className={cn(
                    styles['separator'],
                    stepIndex < lastLineToActivate && styles['active']
                  )}
                />
              )}
            </li>
          )
        })}
      </ul>
    </>
  )
}

export default Stepper
