import cn from 'classnames'

import strokePass from '@/icons/stroke-pass.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './Spinner.module.scss'

/**
 * Props for the Spinner component.
 */
interface SpinnerProps {
  /**
   * A message to display below the spinner.
   * @default 'Chargement en cours'
   */
  message?: string
  /**
   * Custom CSS class for additional styling of the spinner.
   */
  className?: string
  /**
   * A custom test id to target the component when running tests.
   * @default 'spinner'
   */
  testId?: string
}

/**
 * The Spinner component is used to indicate that a process is currently in progress.
 * It displays a loading icon and an optional message.
 *
 * ---
 * **Important: Use the `message` prop to provide context to users on what is being loaded.**
 * ---
 *
 * @param {SpinnerProps} props - The props for the Spinner component.
 * @returns {JSX.Element} The rendered Spinner component.
 *
 * @example
 * <Spinner message="Loading data..." />
 *
 * @accessibility
 * - A descriptive loading message can be provided to help users understand what is being processed.
 */
export const Spinner = ({
  message = 'Chargement en cours',
  className,
  testId = 'spinner',
}: SpinnerProps): JSX.Element => {
  return (
    // biome-ignore lint/a11y/useSemanticElements: We want a `role="status"` here, not an `<output />`.
    <div
      aria-live="polite"
      className={cn(styles['loading-spinner'], className)}
      data-testid={testId}
      role="status"
    >
      <SvgIcon
        src={strokePass}
        alt=""
        className={styles['loading-spinner-icon']}
      />

      <div className={styles['content']}>{message}</div>
    </div>
  )
}
