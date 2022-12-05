import cn from 'classnames'
import React, { ReactNode } from 'react'

import DisabledSvg from './disabled.svg'
import ErrorSvg from './error.svg'
import SuccessSvg from './success.svg'
import styles from './Timeline.module.scss'
import WaitingSvg from './waiting.svg'

export enum TimelineStepType {
  SUCCESS = 'SUCCESS',
  ERROR = 'ERROR',
  WAITING = 'WAITING',
  DISABLED = 'DISABLED',
}

export interface ITimelineStep {
  type: TimelineStepType
  content: ReactNode
}

export interface ITimelineProps {
  steps: ITimelineStep[]
}

const getIconProps = (type: TimelineStepType) => {
  switch (type) {
    case TimelineStepType.SUCCESS:
      return {
        src: SuccessSvg,
        alt: 'Étape en succès',
      }
    case TimelineStepType.ERROR:
      return {
        src: ErrorSvg,
        alt: 'Étape en erreur',
      }
    case TimelineStepType.WAITING:
      return {
        src: WaitingSvg,
        alt: 'Étape en attente',
      }
    case TimelineStepType.DISABLED:
      return {
        src: DisabledSvg,
        alt: 'Étape non disponible',
      }
    default:
      throw new Error(`Unsupported step type: ${type}`)
  }
}

const getLineStyle = (
  stepType: TimelineStepType,
  nextStepType?: TimelineStepType
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
      return styles['line-success']
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
  return (
    <div className={styles.container}>
      {steps.map((step, index) => {
        return (
          <div
            key={index}
            className={cn(
              styles.step,
              getLineStyle(step.type, steps[index + 1]?.type)
            )}
          >
            <img {...getIconProps(step.type)} className={styles.icon} />
            {step.content}
          </div>
        )
      })}
    </div>
  )
}

export default Timeline
