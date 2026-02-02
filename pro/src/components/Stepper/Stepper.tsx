import cn from 'classnames'
import type React from 'react'
import { useRef } from 'react'

import { findLastIndex } from '@/commons/utils/findLastIndex'
import { StepContent } from '@/components/Stepper/StepContent'

import styles from './Stepper.module.scss'

export type Step = {
  id: string
  label: React.ReactNode
  onClick?: (e: React.MouseEvent) => void
  url?: string
  hash?: string
}

export interface StepperProps {
  activeStep: string
  steps: Step[]
  className?: string
}

export const Stepper = ({
  activeStep,
  steps,
  className,
}: StepperProps): JSX.Element => {
  const listRef = useRef<HTMLOListElement>(null)

  const lastStepIndex = steps.length - 1
  const lastLineToActivate = findLastIndex(steps, (step: Step) => !!step.url)

  return (
    // biome-ignore lint/correctness/useUniqueElementIds: We assume stepper is used once per page. There cannot be id duplications.
    <ol
      id="stepper"
      className={cn(styles.stepper, className)}
      data-testid="stepper"
      ref={listRef}
    >
      {steps.map((step, stepIndex) => {
        const isActive = activeStep === step.id
        const isLastStep = lastStepIndex === stepIndex
        const isSelectionnable = !!step.url

        return (
          <li
            {...(isActive ? { id: 'active' } : {})}
            className={cn(
              styles['step-container'],
              isSelectionnable && styles.selectionnable,
              isActive && styles.active
            )}
            key={`step-${step.id}`}
            data-testid={`step-${step.id}`}
          >
            <StepContent step={step} stepIndex={stepIndex} />
            {isActive && (
              <span className={styles['visually-hidden']}>
                {' '}
                (étape en cours)
              </span>
            )}
            {!isLastStep && (
              <div
                className={cn(
                  styles.separator,
                  stepIndex < lastLineToActivate && styles.active
                )}
              />
            )}
          </li>
        )
      })}
    </ol>
  )
}
