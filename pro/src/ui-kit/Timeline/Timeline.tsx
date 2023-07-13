import cn from 'classnames'
import React, { ReactNode } from 'react'

import fullClearIcon from 'icons/full-clear.svg'
import fullValidateIcon from 'icons/full-validate.svg'
import strokeWrongIcon from 'icons/stroke-wrong.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import emptyCircle from './empty-circle.svg'
import styles from './Timeline.module.scss'

export enum TimelineStepType {
  SUCCESS = 'SUCCESS',
  ERROR = 'ERROR',
  WAITING = 'WAITING',
  DISABLED = 'DISABLED',
  CANCELLED = 'CANCELLED',
  REFUSED = 'REFUSED',
}

export interface TimelineStep {
  type: TimelineStepType
  content: ReactNode
}

export interface TimelineProps {
  steps: TimelineStep[]
}

const getIconComponent = (type: TimelineStepType, hasErrorSteps: boolean) => {
  switch (type) {
    case TimelineStepType.SUCCESS:
      return (
        <SvgIcon
          src={fullValidateIcon}
          alt="Étape en succès"
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
        <SvgIcon
          src={fullClearIcon}
          alt="Étape en erreur"
          className={cn(styles.icon, styles['icon-error'])}
        />
      )
    case TimelineStepType.WAITING:
      return (
        <SvgIcon
          src={emptyCircle}
          alt="Étape en attente"
          className={cn(styles.icon, styles['icon-waiting'])}
          viewBox="0 0 21 20"
        />
      )
    case TimelineStepType.DISABLED:
      return (
        <SvgIcon
          src={emptyCircle}
          alt="Étape non disponible"
          className={cn(styles.icon, styles['icon-disabled'])}
          viewBox="0 0 21 20"
        />
      )
    case TimelineStepType.CANCELLED:
      return (
        <SvgIcon
          src={fullClearIcon}
          alt="Étape annulée"
          className={cn(styles.icon, styles['icon-error'])}
        />
      )
    case TimelineStepType.REFUSED:
      return (
        <SvgIcon
          src={strokeWrongIcon}
          className={cn(styles.icon, styles['icon-wrong'])}
          alt="Étape refusée"
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

const Timeline = ({ steps }: TimelineProps): JSX.Element => {
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
