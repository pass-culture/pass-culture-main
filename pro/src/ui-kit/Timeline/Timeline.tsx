import cn from 'classnames'
import { ReactNode } from 'react'

import fullClearIcon from 'icons/full-clear.svg'
import fullEllipseIcon from 'icons/full-ellipse.svg'
import fullValidateIcon from 'icons/full-validate.svg'
import strokeWrongIcon from 'icons/stroke-wrong.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

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
 * @returns {JSX.Element} The icon component for the timeline step.
 */
const getIconComponent = (type: TimelineStepType) => {
  switch (type) {
    case TimelineStepType.SUCCESS:
      return (
        <SvgIcon
          src={fullValidateIcon}
          alt="Étape en succès"
          className={cn(styles.icon, styles['icon-success'])}
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
          src={fullEllipseIcon}
          alt="Étape en attente"
          className={cn(styles.icon, styles['icon-waiting'])}
        />
      )
    case TimelineStepType.DISABLED:
      return (
        <SvgIcon
          src={fullEllipseIcon}
          alt="Étape non disponible"
          className={cn(styles.icon, styles['icon-disabled'])}
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
 * @returns {string | null} The line style for the timeline step.
 */
const getLineStyle = (
  stepType: TimelineStepType,
  nextStepType?: TimelineStepType
) => {
  // No line if last step
  if (nextStepType === undefined) {
    return undefined
  }

  if (stepType === TimelineStepType.SUCCESS) {
    return cn(styles['line'], styles['line-success'])
  }

  // The type of the line is always the type of the 2nd step, with one exception:
  // the "waiting" type has always "waiting" lines around it on both sides
  if (stepType === TimelineStepType.WAITING) {
    return cn(styles['line'], styles['line-waiting'])
  }

  switch (nextStepType) {
    case TimelineStepType.SUCCESS:
      return cn(styles['line'], styles['line-success'])
    case TimelineStepType.ERROR:
      return cn(styles['line'], styles['line-error'])
    case TimelineStepType.WAITING:
      return cn(styles['line'], styles['line-waiting'])
    case TimelineStepType.DISABLED:
      return cn(styles['line'], styles['line-disabled'])
    case TimelineStepType.CANCELLED:
    case TimelineStepType.REFUSED:
    default:
      return undefined
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
  return (
    <ol className={styles.container}>
      {steps.map((step, index) => {
        const nextStepType = steps[index + 1]?.type
        return (
          <li key={index} className={styles['step']}>
            <div className={styles['icon-line-container']}>
              <div className={styles['icon-container']}>
                {getIconComponent(step.type)}
              </div>
              <div className={getLineStyle(step.type, nextStepType)} />
            </div>
            <div className={styles['step-content']}>{step.content}</div>
          </li>
        )
      })}
    </ol>
  )
}
