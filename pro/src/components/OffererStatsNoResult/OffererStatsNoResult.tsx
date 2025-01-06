import cn from 'classnames'

import strokePieIcon from 'icons/stroke-pie.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './OffererStatsNoResult.module.scss'

type OffererStatsNoResultProps = {
  title: string
  subtitle: string
  extraClassName?: string
}

export const OffererStatsNoResult = ({
  title,
  subtitle,
  extraClassName,
}: OffererStatsNoResultProps) => {
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
