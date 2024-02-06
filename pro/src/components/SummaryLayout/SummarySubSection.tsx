import cn from 'classnames'
import React from 'react'

import { Title } from 'ui-kit'

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
    <Title
      as="h4"
      className={style['summary-layout-sub-section-title']}
      level={4}
    >
      {title}
    </Title>
    {children}
    <div className={style['summary-layout-sub-section-separator']}></div>
  </div>
)
