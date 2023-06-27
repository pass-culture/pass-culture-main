import cn from 'classnames'
import React, { ReactNode } from 'react'

import styles from './Tooltip.module.scss'

export interface TooltipProps {
  id: string // Mandatory, must be linked to the aria-describedby attribute of the child
  content: ReactNode
  children: ReactNode
  className?: string
}

const Tooltip = ({
  id,
  children,
  content,
  className,
}: TooltipProps): JSX.Element => {
  return (
    <div className={cn(styles['tooltip-container'], className)}>
      {children}
      <div className={styles.tooltip} role="tooltip" id={id}>
        {content}
      </div>
    </div>
  )
}

export default Tooltip
