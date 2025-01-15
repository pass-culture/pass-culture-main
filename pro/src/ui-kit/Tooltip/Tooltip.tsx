import cn from 'classnames'
import { ReactNode } from 'react'

import styles from './Tooltip.module.scss'

/**
 * Props for the Tooltip component.
 */
interface TooltipProps {
  /**
   * The content to be displayed inside the tooltip.
   */
  content: ReactNode
  /**
   * The children element that the tooltip is attached to.
   */
  children: ReactNode
  /**
   * Custom CSS class for the tooltip container.
   */
  tooltipContainerClassName?: string
  /**
   * Custom CSS class for the tooltip content.
   */
  tooltipContentClassName?: string
  /**
   * Determines if the tooltip should be visually hidden.
   */
  visuallyHidden: boolean
}

/**
 * The Tooltip component is used to display additional information when a user hovers over or focuses on an element.
 * It wraps around a child element and shows the tooltip content when triggered.
 *
 * ---
 * **Important: Ensure the `content` prop provides meaningful information to assist users.**
 * ---
 *
 * @param {TooltipProps} props - The props for the Tooltip component.
 * @returns {JSX.Element} The rendered Tooltip component.
 *
 * @example
 * <Tooltip content="This is a tooltip">
 *   <button>Hover over me</button>
 * </Tooltip>
 *
 * @accessibility
 * - **Tooltip Visibility**: Use the `visuallyHidden` prop to control when the tooltip is displayed.
 * - **ARIA Role**: The tooltip uses `role="tooltip"` to ensure that it is recognized by assistive technologies.
 * - **Event Handling**: Implement `onMouseOver`, `onMouseOut`, `onFocus`, `onBlur`, and `onKeyDown` handlers for accessibility.
 */
export const Tooltip = ({
  children,
  content,
  tooltipContainerClassName,
  tooltipContentClassName,
  visuallyHidden,
}: TooltipProps): JSX.Element => {
  return (
    <span
      className={cn(styles['tooltip-container'], tooltipContainerClassName)}
    >
      {children}
      <span
        className={cn(
          styles['tooltip'],
          {
            [styles['tooltip-hidden']]: visuallyHidden,
          },
          tooltipContentClassName
        )}
        role="tooltip"
      >
        {content}
      </span>
    </span>
  )
}
