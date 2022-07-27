import cn from 'classnames'
import React from 'react'

import style from './SummaryLayout.module.scss'

interface ISummaryLayoutContentProps {
  className?: string
  children?: React.ReactNode | React.ReactNode[]
}

const Content = ({
  className,
  children,
}: ISummaryLayoutContentProps): JSX.Element => (
  <div className={cn(style['summary-layout-content'], className)}>
    {children}
  </div>
)

export default Content
