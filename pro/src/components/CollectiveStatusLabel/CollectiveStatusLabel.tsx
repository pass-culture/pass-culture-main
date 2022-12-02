import cn from 'classnames'
import React, { ReactElement } from 'react'

import style from './CollectiveStatusLabel.module.scss'
type ICollectiveStatusLabelProps = {
  className: string
  icon: ReactElement
  label: string
}

const CollectiveStatusLabel = ({
  className,
  icon,
  label,
}: ICollectiveStatusLabelProps) => {
  return (
    <span className={cn(style['status-label'], className)}>
      <>
        {icon}
        {label}
      </>
    </span>
  )
}
export default CollectiveStatusLabel
