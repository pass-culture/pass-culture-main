import cn from 'classnames'
import React, { ReactElement } from 'react'

import style from './CollectiveStatusLabel.module.scss'
type CollectiveStatusLabelProps = {
  className: string
  icon: ReactElement
  label: string
}

export const CollectiveStatusLabel = ({
  className,
  icon,
  label,
}: CollectiveStatusLabelProps) => {
  return (
    <span className={cn(style['status-label'], className)}>
      <>
        {icon}
        {label}
      </>
    </span>
  )
}
