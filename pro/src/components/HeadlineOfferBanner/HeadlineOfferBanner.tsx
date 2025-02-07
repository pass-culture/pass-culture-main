import { useHeadlineOfferContext } from 'commons/context/HeadlineOfferContext/HeadlineOfferContext'
import strokeCloseIcon from 'icons/stroke-close.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import imgHeadlineOffer from './assets/headlineOffer.png'
import { HeadlineOfferInformationDialog } from './components/HeadlineOfferInformationDialog'
import styles from './HeadlineOfferBanner.module.scss'

export const HeadlineOfferBanner = () => {
  const { isHeadlineOfferBannerOpen, closeHeadlineOfferBanner } = useHeadlineOfferContext()

  if (!isHeadlineOfferBannerOpen) {
    return null
  }

  return (
    <div className={styles['headline-offer-banner']}>
      <div className={styles['headline-offer-text-container']}>
        <p className={styles['headline-offer-title']}>
          <span aria-hidden="true">✨</span> Nouvelle fonctionnalité : l’offre à
          la une !{' '}
        </p>
        <p className={styles['headline-offer-description']}>
          Votre offre à la une sera mise en avant sur votre page sur
          l’application.
        </p>
        <HeadlineOfferInformationDialog />
      </div>
      <img
        className={styles['headline-offer-img']}
        alt=""
        src={imgHeadlineOffer}
        role="presentation"
      />
      <div>
        <Button
          className={styles['headline-offer-close-button']}
          variant={ButtonVariant.TERNARY}
          icon={strokeCloseIcon}
          iconAlt="Fermer la bannière"
          onClick={closeHeadlineOfferBanner}
        />
      </div>
    </div>
  )
}
