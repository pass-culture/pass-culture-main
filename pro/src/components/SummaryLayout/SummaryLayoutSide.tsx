import cn from 'classnames'
import React from 'react'

import style from './SummaryLayout.module.scss'

interface ISummaryLayoutSideProps {
  className?: string
  children?: React.ReactNode | React.ReactNode[]
}

const Side = ({
  className,
  children,
}: ISummaryLayoutSideProps): JSX.Element => (
  <div className={cn(style['summary-layout-side'], className)}>{children}</div>
)

export default Side
