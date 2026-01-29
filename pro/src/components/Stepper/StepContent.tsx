import { Link } from 'react-router'

import type { Step } from './Stepper'
import styles from './Stepper.module.scss'

interface StepContentProps {
  step: Step
  stepIndex: number
}

export const StepContent = ({
  step,
  stepIndex,
}: StepContentProps): JSX.Element => {
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
