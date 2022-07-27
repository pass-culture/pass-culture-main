import cn from 'classnames'
import React from 'react'

import style from './SummaryLayout.module.scss'

interface ISummaryLayoutRowProps {
  className?: string
  description: string | number
  title?: string
}

const Row = ({
  className,
  description,
  title,
}: ISummaryLayoutRowProps): JSX.Element => (
  <div className={cn(style['summary-layout-row'], className)}>
    <span className={style['summary-layout-row-title']}>
      {title}
      {title && ' : '}
    </span>
    <span>{description}</span>
  </div>
)

export default Row
