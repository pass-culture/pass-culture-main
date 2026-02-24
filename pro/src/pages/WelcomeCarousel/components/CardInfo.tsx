import type React from 'react'

import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './CardInfo.module.scss'

type CardInfoProps = {
  icon: string
  title: string
  children?: React.ReactNode
}
export const CardInfo = ({
  icon,
  title,
  children,
}: CardInfoProps): JSX.Element => (
  <div className={styles[`card-info`]}>
    <div className={styles[`card-info-header`]}>
      <div className={styles['card-info-icon-wrapper']}>
        <SvgIcon src={icon} className={styles['card-info-icon']} />
      </div>
      <h3 className={styles[`card-info-header-title`]}>{title}</h3>
    </div>

    <div className={styles['card-info-description']}>{children}</div>
  </div>
)
