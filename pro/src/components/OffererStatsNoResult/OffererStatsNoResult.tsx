import cn from 'classnames'
import React from 'react'

import strokePieIcon from 'icons/stroke-pie.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './OffererStatsNoResult.module.scss'

type OffererStatsNoResult = {
  title: string
  subtitle: string
  extraClassName?: string
}

const OffererStatsNoResult = ({
  title,
  subtitle,
  extraClassName,
}: OffererStatsNoResult) => {
  return (
    <div
      className={cn(
        styles['offerer-stats-no-result-container'],
        extraClassName
      )}
    >
      <SvgIcon
        src={strokePieIcon}
        alt=""
        className={styles['offerer-stats-no-result-icon']}
      />
      <h4 className={styles['title']}>{title}</h4>
      <p>{subtitle}</p>
    </div>
  )
}

export default OffererStatsNoResult
