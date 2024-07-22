import cn from 'classnames'
import React from 'react'

import style from './SummaryLayout.module.scss'

interface SummaryLayoutContentProps {
  className?: string
  children?: React.ReactNode | React.ReactNode[]
  fullWidth?: boolean
}

export const SummaryContent = ({
  className,
  children,
  fullWidth = false,
}: SummaryLayoutContentProps): JSX.Element => (
  <div
    className={cn(style['summary-layout-content'], className, {
      [style['full-width'] ?? '']: fullWidth,
    })}
  >
    {children}
  </div>
)
