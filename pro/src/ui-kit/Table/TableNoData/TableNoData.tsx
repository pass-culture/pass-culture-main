import type { ReactNode } from 'react'

import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './TableNoData.module.scss'

interface TableNoDataProps {
  noData: {
    icon: string
    title: string
    subtitle: string
    cta?: ReactNode
  }
}

export const TableNoData = ({
  noData: { icon, title, subtitle, cta },
}: TableNoDataProps): JSX.Element => {
  return (
    <div className={styles['no-data']}>
      <SvgIcon
        src={icon}
        alt=""
        width="80"
        className={styles['no-data-icon']}
      />
      <p className={styles['no-data-title']}>{title}</p>
      <p className={styles['no-data-subtitle']}>{subtitle}</p>
      <div className={styles['no-data-cta']}>{cta}</div>
    </div>
  )
}
