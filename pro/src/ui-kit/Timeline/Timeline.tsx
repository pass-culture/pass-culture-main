import cn from 'classnames'
import React, { ReactNode } from 'react'

import { ReactComponent as ErrorSvg } from 'icons/ico-clear.svg'
import { ReactComponent as SuccessSvg } from 'icons/ico-notification-success.svg'

import { ReactComponent as DisabledSvg } from './disabled.svg'
import styles from './Timeline.module.scss'
import { ReactComponent as WaitingSvg } from './waiting.svg'

export enum TimelineStepType {
  SUCCESS = 'SUCCESS',
  ERROR = 'ERROR',
  WAITING = 'WAITING',
  DISABLED = 'DISABLED',
  CANCELLED = 'CANCELLED',
}

export interface ITimelineStep {
  type: TimelineStepType
  content: ReactNode
}

export interface ITimelineProps {
  steps: ITimelineStep[]
}

const getIconComponent = (type: TimelineStepType, hasErrorSteps: boolean) => {
  switch (type) {
    case TimelineStepType.SUCCESS:
      return (
        <SuccessSvg
          title="Étape en succès"
          className={cn(
            styles.icon,
            hasErrorSteps
              ? styles['icon-success-disabled']
              : styles['icon-success']
          )}
        />
      )
    case TimelineStepType.ERROR:
      return (
        <ErrorSvg
          title="Étape en erreur"
          className={cn(styles.icon, styles['icon-error'])}
        />
      )
    case TimelineStepType.WAITING:
      return (
        <WaitingSvg
          title="Étape en attente"
          className={cn(styles.icon, styles['icon-waiting'])}
        />
      )
    case TimelineStepType.DISABLED:
      return (
        <DisabledSvg
          title="Étape non disponible"
          className={cn(styles.icon, styles['icon-disabled'])}
        />
      )
    case TimelineStepType.CANCELLED:
      return (
        <ErrorSvg
          title="Étape annulée"
          className={cn(styles.icon, styles['icon-error'])}
        />
      )
    default:
      throw new Error(`Unsupported step type: ${type}`)
  }
}

const getLineStyle = (
  stepType: TimelineStepType,
  nextStepType?: TimelineStepType,
  hasErrorSteps?: boolean
) => {
  // No line if last step
  if (nextStepType === undefined) {
    return null
  }

  // The type of the line is always the type of the 2nd step, with one exception:
  // the "waiting" type has always "waiting" lines around it on both sides
  if (stepType === TimelineStepType.WAITING) {
    return styles['line-waiting']
  }

  switch (nextStepType) {
    case TimelineStepType.SUCCESS:
      return hasErrorSteps ? styles['line-error'] : styles['line-success']
    case TimelineStepType.ERROR:
      return styles['line-error']
    case TimelineStepType.WAITING:
      return styles['line-waiting']
    case TimelineStepType.DISABLED:
      return styles['line-disabled']
    default:
      throw new Error(`Unsupported step type: ${nextStepType}`)
  }
}

const Timeline = ({ steps }: ITimelineProps): JSX.Element => {
  const hasErrorSteps =
    steps.filter(x => x.type === TimelineStepType.ERROR).length > 0
  return (
    <ol className={styles.container}>
      {steps.map((step, index) => {
        return (
          <li
            key={index}
            className={cn(
              styles.step,
              getLineStyle(step.type, steps[index + 1]?.type, hasErrorSteps)
            )}
          >
            {getIconComponent(step.type, hasErrorSteps)}
            {step.content}
          </li>
        )
      })}
    </ol>
  )
}

export default Timeline
