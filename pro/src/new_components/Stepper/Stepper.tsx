import cn from 'classnames'
import React from 'react'

import type { Step } from 'new_components/Breadcrumb'
import StepContent from 'new_components/Stepper/StepContent'
import { findLastIndex } from 'utils/findLastIndex'

import styles from './Stepper.module.scss'

export interface IStepper {
  activeStep: string
  steps: Step[]
  className?: string
}

const Stepper = ({ activeStep, steps, className }: IStepper): JSX.Element => {
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
