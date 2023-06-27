import cn from 'classnames'
import React from 'react'

import style from './SummaryLayout.module.scss'

interface SummaryLayoutRowProps {
  className?: string
  description: string | number | React.ReactNode
  title?: string
}

const Row = ({
  className,
  description,
  title,
}: SummaryLayoutRowProps): JSX.Element => (
  <div className={cn(style['summary-layout-row'], className)}>
    <span className={style['summary-layout-row-title']}>
      {title}
      {title && ' : '}
    </span>
    <span className={style['summary-layout-row-description']}>
      {description}
    </span>
  </div>
)

export default Row
