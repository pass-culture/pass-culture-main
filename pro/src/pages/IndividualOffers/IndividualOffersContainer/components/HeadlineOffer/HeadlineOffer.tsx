import { useHeadlineOfferContext } from 'commons/context/HeadlineOfferContext/HeadlineOfferContext'
import { WEBAPP_URL } from 'commons/utils/config'
import fullLinkIcon from 'icons/full-link.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Thumb } from 'ui-kit/Thumb/Thumb'

import styles from './HeadlineOffer.module.scss'

export function HeadlineOffer() {
  const { isHeadlineOfferAllowedForOfferer, headlineOffer } =
    useHeadlineOfferContext()

  if (!isHeadlineOfferAllowedForOfferer || !headlineOffer) {
    return
  }

  const venuePreviewLink = `${WEBAPP_URL}/lieu/${headlineOffer.venueId}`

  return (
    <div className={styles['headline-offer-container']}>
      <div className={styles['headline-offer-title-container']}>
        <h2 className={styles['headline-offer-title']}>Votre offre à la une</h2>
        <ButtonLink
          variant={ButtonVariant.QUATERNARY}
          icon={fullLinkIcon}
          to={venuePreviewLink}
          isExternal
          opensInNewTab
        >
          Visualiser dans l’application
        </ButtonLink>
      </div>

      <div className={styles['headline-offer-block']}>
        <Thumb
          className={styles['headline-offer-thumb']}
          url={headlineOffer.image?.url}
        />
        <p className={styles['headline-offer-name']}>{headlineOffer.name}</p>
      </div>
    </div>
  )
}
