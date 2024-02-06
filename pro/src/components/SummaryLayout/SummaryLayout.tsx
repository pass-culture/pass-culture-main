import cn from 'classnames'
import React from 'react'

import style from './SummaryLayout.module.scss'

interface SummaryLayoutProps {
  children?: React.ReactNode | React.ReactNode[]
  className?: string
}

export const SummaryLayout = ({
  children,
  className,
}: SummaryLayoutProps): JSX.Element => (
  <div className={cn(style['summary-layout'], className)}>{children}</div>
)
