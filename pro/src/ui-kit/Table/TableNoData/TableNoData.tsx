import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './TableNoData.module.scss'

interface TableNoDataProps {
  noData: {
    icon: string
    title: string
    subtitle: string
  }
}

export const TableNoData = ({
  noData: { icon, title, subtitle },
}: TableNoDataProps): JSX.Element => {
  return (
    <div className={styles['no-data']}>
      <SvgIcon
        src={icon}
        alt=""
        width="100"
        className={styles['no-data-icon']}
      />
      <p className={styles['no-data-title']}>{title}</p>
      <p className={styles['no-data-subtitle']}>{subtitle}</p>
    </div>
  )
}
