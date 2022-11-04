import cn from 'classnames'
import React from 'react'

import { Title } from 'ui-kit'

import style from './SummaryLayout.module.scss'

interface ISummaryLayoutSubSectionProps {
  title: string
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

const SubSection = ({
  title,
  children,
  className,
}: ISummaryLayoutSubSectionProps): JSX.Element => (
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

export default SubSection
