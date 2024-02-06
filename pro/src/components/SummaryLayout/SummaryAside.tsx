import cn from 'classnames'
import React from 'react'

import style from './SummaryLayout.module.scss'

interface SummaryLayoutSideProps {
  className?: string
  children?: React.ReactNode | React.ReactNode[]
}

export const SummaryAside = ({
  className,
  children,
}: SummaryLayoutSideProps): JSX.Element => (
  <div className={cn(style['summary-layout-side'], className)}>{children}</div>
)
