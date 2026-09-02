import type { EmptyStateProps } from 'ui-kit/Table/Table'

import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './TableNoData.module.scss'

export const TableNoData = ({
  noData,
}: {
  noData: EmptyStateProps
}): JSX.Element => {
  const { icon, title, subtitle, cta } = noData.message
  return (
    <div className={styles['no-data']} role="status">
      {noData.hasNoData ? (
        <>
          <SvgIcon
            src={icon}
            alt=""
            width="80"
            className={styles['no-data-icon']}
            aria-hidden={true}
          />
          <p className={styles['no-data-title']}>{title}</p>
          {subtitle && <p className={styles['no-data-subtitle']}>{subtitle}</p>}
          <div className={styles['no-data-cta']}>{cta}</div>
        </>
      ) : (
        <span>&nbsp;</span>
      )}
    </div>
  )
}
