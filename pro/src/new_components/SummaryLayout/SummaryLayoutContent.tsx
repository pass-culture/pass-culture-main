import cn from 'classnames'
import React from 'react'

import style from './SummaryLayout.module.scss'

interface ISummaryLayoutContentProps {
  className?: string
  children?: React.ReactNode | React.ReactNode[]
  fullWidth?: boolean
}

const Content = ({
  className,
  children,
  fullWidth = false,
}: ISummaryLayoutContentProps): JSX.Element => (
  <div
    className={cn(style['summary-layout-content'], className, {
      [style['full-width']]: fullWidth,
    })}
  >
    {children}
  </div>
)

export default Content
