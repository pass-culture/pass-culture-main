import React from 'react'
import { Link } from 'react-router-dom'

import { Step } from './Stepper'
import styles from './Stepper.module.scss'

interface StepContent {
  step: Step
  stepIndex: number
  stepsCount: number
  stepperWidth?: number
}

export const StepContent = ({
  step,
  stepIndex,
  stepsCount,
  stepperWidth,
}: StepContent): JSX.Element => {
  const stepContent = (
    <>
      <div className={styles['number']}>
        <div className={styles['inner']}>{stepIndex + 1}</div>
      </div>
      <div
        className={styles['label']}
        style={{
          //  Give a width to the label based on the total width available
          width: `${(stepperWidth ?? stepsCount * 100) / (stepsCount + 1)}px`,
        }}
      >
        <div className={styles['inner']}>
          <span>{step.label}</span>
        </div>
      </div>
    </>
  )
  return step.url ? (
    <Link
      className={styles['step']}
      onClick={step.onClick ? step.onClick : undefined}
      to={step.url}
    >
      {stepContent}
    </Link>
  ) : (
    <div className={styles['step']}>{stepContent}</div>
  )
}
