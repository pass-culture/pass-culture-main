import React from 'react'
import { Title } from 'ui-kit'
import cn from 'classnames'
import style from './SummaryLayout.module.scss'

interface ISummaryLayoutSectionProps {
  title: string
  children: React.ReactNode | React.ReactNode[]
  className?: string
}

const Section = ({
  title,
  children,
  className,
}: ISummaryLayoutSectionProps): JSX.Element => (
  <div className={cn(style['summary-layout-section'], className)}>
    <div className={style['summary-layout-section-header']}>
      <Title as="h3" level={3}>
        {title}
      </Title>
      <div className={style['summary-layout-section-header-separator']}></div>
    </div>
    {children}
  </div>
)

export default Section
