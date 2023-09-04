import cn from 'classnames'
import React, { ReactNode } from 'react'

import styles from './Tooltip.module.scss'

export interface TooltipProps {
  content: ReactNode
  children: ReactNode
  className?: string
  visuallyHidden: boolean
}

const Tooltip = ({
  children,
  content,
  className,
  visuallyHidden,
}: TooltipProps): JSX.Element => {
  // Tooltip should implement onMouseOver onMouseOut onFocus onBlur onKeyDown
  // on parent to be accessible
  return (
    <div className={cn(styles['tooltip-container'], className)}>
      {children}
      <div
        className={cn(styles['tooltip'], {
          ['visually-hidden']: visuallyHidden,
        })}
        role="tooltip"
      >
        {content}
      </div>
    </div>
  )
}

export default Tooltip
