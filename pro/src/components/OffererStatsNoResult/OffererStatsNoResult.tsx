import cn from 'classnames'
import React from 'react'

import styles from './OffererStatsNoResult.module.scss'

type OffererStatsNoResult = {
  title: string
  subtitle: string
  extraClassName?: string
  icon?: React.ComponentProps<any>
}

const OffererStatsNoResult = ({
  title,
  subtitle,
  icon,
  extraClassName,
}: OffererStatsNoResult) => {
  return (
    <div
      className={cn(
        styles['offerer-stats-no-result-container'],
        extraClassName
      )}
    >
      {icon}
      <h4 className={styles['title']}>{title}</h4>
      <p>{subtitle}</p>
    </div>
  )
}

export default OffererStatsNoResult
