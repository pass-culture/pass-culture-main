import React from 'react'
import { Link } from 'react-router-dom'

import type { Step } from 'components/Breadcrumb'

import styles from './Stepper.module.scss'

interface StepContent {
  step: Step
  stepIndex: number
}

const StepContent = ({ step, stepIndex }: StepContent): JSX.Element => {
  const stepContent = (
    <>
      <div className={styles['number']}>
        <div className={styles['inner']}>{stepIndex + 1}</div>
      </div>
      <div className={styles['label']}>
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

export default StepContent
