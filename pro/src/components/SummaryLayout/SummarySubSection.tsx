import cn from 'classnames'
import React from 'react'

import { Divider } from 'ui-kit/Divider/Divider'

import style from './SummaryLayout.module.scss'

interface SummaryLayoutSubSectionProps {
  title: string
  children: React.ReactNode | React.ReactNode[]
  className?: string
  shouldShowDivider?: boolean
}

export const SummarySubSection = ({
  title,
  children,
  className,
  shouldShowDivider = true,
}: SummaryLayoutSubSectionProps): JSX.Element => (
  <div className={cn(style['summary-layout-sub-section'], className)}>
    <h3 className={style['summary-layout-sub-section-title']}>{title}</h3>
    {children}
    {shouldShowDivider && <Divider size="large" />}
  </div>
)
