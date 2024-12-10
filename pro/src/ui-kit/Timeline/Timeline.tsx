import cn from 'classnames'
import React, { ReactNode } from 'react'

import fullClearIcon from 'icons/full-clear.svg'
import fullValidateIcon from 'icons/full-validate.svg'
import strokeWrongIcon from 'icons/stroke-wrong.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import emptyCircle from './empty-circle.svg'
import styles from './Timeline.module.scss'

/**
 * Enum for the types of steps in the timeline.
 */
export enum TimelineStepType {
  SUCCESS = 'SUCCESS',
  ERROR = 'ERROR',
  WAITING = 'WAITING',
  DISABLED = 'DISABLED',
  CANCELLED = 'CANCELLED',
  REFUSED = 'REFUSED',
}

/**
 * Represents a single step in the timeline.
 */
export interface TimelineStep {
  /**
   * The type of the timeline step.
   */
  type: TimelineStepType
  /**
   * The content to be displayed inside the timeline step.
   */
  content: ReactNode
}

/**
 * Props for the Timeline component.
 */
interface TimelineProps {
  /**
   * An array of timeline steps to be displayed.
   */
  steps: TimelineStep[]
}

/**
 * Gets the appropriate icon component for a given timeline step type.
 *
 * @param {TimelineStepType} type - The type of the timeline step.
 * @param {boolean} hasErrorSteps - Indicates if there are error steps in the timeline.
 * @returns {JSX.Element} The icon component for the timeline step.
 */
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

/**
 * Gets the appropriate line style for the timeline based on the step type and the next step type.
 *
 * @param {TimelineStepType} stepType - The type of the current step.
 * @param {TimelineStepType} [nextStepType] - The type of the next step.
 * @param {boolean} [hasErrorSteps] - Indicates if there are error steps in the timeline.
 * @returns {string | null} The line style for the timeline step.
 */
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
    case TimelineStepType.CANCELLED:
    case TimelineStepType.REFUSED:
    default:
      throw new Error(`Unsupported step type: ${nextStepType}`)
  }
}

/**
 * The Timeline component is used to display a sequence of steps in a timeline.
 * Each step can represent different statuses such as success, error, waiting, etc.
 *
 * ---
 * **Important: Use the `steps` prop to provide the list of steps in the timeline.**
 * ---
 *
 * @param {TimelineProps} props - The props for the Timeline component.
 * @returns {JSX.Element} The rendered Timeline component.
 *
 * @example
 * <Timeline
 *   steps={[
 *     { type: TimelineStepType.SUCCESS, content: 'Step 1 completed' },
 *     { type: TimelineStepType.ERROR, content: 'Step 2 failed' },
 *     { type: TimelineStepType.WAITING, content: 'Step 3 pending' }
 *   ]}
 * />
 *
 * @accessibility
 * - **Icons and Labels**: Icons are used to represent the status of each step, with appropriate `alt` attributes for context.
 * - **Visual Indicators**: The component uses different colors and icons to indicate the status of each step, making it easy to understand at a glance.
 */
export const Timeline = ({ steps }: TimelineProps): JSX.Element => {
  const hasErrorSteps =
    steps.filter((x) => x.type === TimelineStepType.ERROR).length > 0
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
