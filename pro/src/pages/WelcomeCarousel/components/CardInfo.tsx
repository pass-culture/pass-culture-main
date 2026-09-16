import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './CardInfo.module.scss'

type CardInfoProps = {
  icon: string
  title: string
  description: string
}
export const CardInfo = ({
  icon,
  title,
  description,
}: CardInfoProps): JSX.Element => (
  <div className={styles['card-info']}>
    <div className={styles['card-info-header']}>
      <div className={styles['card-info-icon-wrapper']}>
        <SvgIcon src={icon} className={styles['card-info-icon']} />
      </div>
      <h3 className={styles['card-info-header-title']}>{title}</h3>
    </div>

    <p className={styles['card-info-description']}>{description}</p>
  </div>
)
