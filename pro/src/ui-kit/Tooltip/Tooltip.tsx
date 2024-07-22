import cn from 'classnames'
import React, { ReactNode } from 'react'

import styles from './Tooltip.module.scss'

interface TooltipProps {
  content: ReactNode
  children: ReactNode
  tooltipContainerClassName?: string
  tooltipContentClassName?: string
  visuallyHidden: boolean
}

export const Tooltip = ({
  children,
  content,
  tooltipContainerClassName,
  tooltipContentClassName,
  visuallyHidden,
}: TooltipProps): JSX.Element => {
  // Tooltip should implement onMouseOver onMouseOut onFocus onBlur onKeyDown
  // on parent to be accessible
  return (
    <span
      className={cn(styles['tooltip-container'], tooltipContainerClassName)}
    >
      {children}
      <span
        className={cn(
          styles['tooltip'],
          {
            [styles['tooltip-hidden'] ?? '']: visuallyHidden,
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
