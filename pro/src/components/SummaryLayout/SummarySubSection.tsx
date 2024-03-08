import cn from 'classnames'
import React from 'react'

import style from './SummaryLayout.module.scss'

interface SummaryLayoutSubSectionProps {
  title: string
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

export const SummarySubSection = ({
  title,
  children,
  className,
}: SummaryLayoutSubSectionProps): JSX.Element => (
  <div className={cn(style['summary-layout-sub-section'], className)}>
    <h3 className={style['summary-layout-sub-section-title']}>{title}</h3>

    {children}
  </div>
)
