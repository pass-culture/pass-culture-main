import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullLinkIcon from '@/icons/full-link.svg'
import strokeBookingHoldIcon from '@/icons/stroke-booking-hold.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './CumulatedViews.module.scss'

const BEST_PRACTICES_URL =
  'https://passcultureapp.notion.site/Les-bonnes-pratiques-et-tudes-du-pass-Culture-323b1a0ec309406192d772e7d803fbd0'

export const CumulatedViewsEmptyState = () => {
  return (
    <div className={styles['no-data']}>
      <SvgIcon
        className={styles['no-data-icon']}
        src={strokeBookingHoldIcon}
        alt=""
        width="128"
      />

      <div className={styles['no-data-caption']}>
        Vos offres n’ont pas encore été découvertes par les bénéficiaires
      </div>

      <div>
        Inspirez-vous des conseils de nos équipes pour améliorer la visibilité
        de vos offres
      </div>

      <div>
        <Button
          as="a"
          to={BEST_PRACTICES_URL}
          isExternal
          opensInNewTab
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
          icon={fullLinkIcon}
          label="Bonnes pratiques de création d'offres"
        />
      </div>
    </div>
  )
}
