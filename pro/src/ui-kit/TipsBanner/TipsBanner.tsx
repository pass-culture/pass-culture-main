import cn from 'classnames'

import fullBulbIcon from '@/icons/full-bulb.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './TipsBanner.module.scss'

export interface TipsBannerProps {
  /**
   * The content to display inside the TipsBanner.
   */
  children: React.ReactNode
  /**
   * An optional decorative image.
   */
  decorativeImage?: string
  /**
   * Extra classnames to apply to the TipsBanner.
   */
  className?: string
}

export const TipsBanner = ({
  decorativeImage,
  children,
  className,
}: TipsBannerProps): JSX.Element => {
  return (
    <div className={cn(className, styles['tips-banner'])}>
      <div className={styles['tips-banner-text']}>
        <div className={styles['tips-banner-header']}>
          <SvgIcon src={fullBulbIcon} className={styles['tips-banner-icon']} />À
          savoir
        </div>
        <div className={styles['tips-banner-content']}>{children}</div>
      </div>
      {decorativeImage && (
        <img
          className={styles['tips-banner-illustration']}
          src={decorativeImage}
          alt=""
        />
      )}
    </div>
  )
}
