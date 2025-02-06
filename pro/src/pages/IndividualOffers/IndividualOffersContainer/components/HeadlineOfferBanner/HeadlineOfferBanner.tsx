import strokeCloseIcon from 'icons/stroke-close.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import imgHeadlineOffer from './assets/headlineOffer.png'
import { HeadlineOfferInformationDialog } from './components/HeadlineOfferInformationDialog'
import styles from './HeadlineOfferBanner.module.scss'

type HeadlineOfferBannerProps = {
  close: () => void
}

export const HeadlineOfferBanner = ({ close }: HeadlineOfferBannerProps) => {
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
          onClick={close}
        />
      </div>
    </div>
  )
}
