import fullBulbIcon from 'icons/full-bulb.svg'
import fullLinkIcon from 'icons/full-link.svg'
import { ButtonLink, LinkProps } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './TipsBanner.module.scss'

export interface TipsBannerProps {
  /**
   * The content to display inside the TipsBanner.
   */
  children: React.ReactNode
  /**
   * An optional link to include in the TipsBanner.
   */
  link?: LinkProps & {
    /**
     * The text to display for the link.
     */
    text: string
  }
  /**
   * An optional decorative image.
   */
  decorativeImage?: string
}

export const TipsBanner = ({
  link,
  decorativeImage,
  children,
}: TipsBannerProps): JSX.Element => {
  return (
    <div className={styles['tips-banner']}>
      <div className={styles['tips-banner-text']}>
        <div className={styles['tips-banner-header']}>
          <SvgIcon src={fullBulbIcon} className={styles['tips-banner-icon']} />À
          savoir
        </div>
        <div className={styles['tips-banner-content']}>{children}</div>
        {link && (
          <ButtonLink
            {...link}
            icon={fullLinkIcon}
            className={styles['tips-banner-link']}
            variant={ButtonVariant.QUATERNARY}
          >
            {link.text}
          </ButtonLink>
        )}
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
