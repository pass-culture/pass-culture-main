import { useState } from 'react'
import { useLocation } from 'react-router-dom'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import fullNextIcon from 'icons/full-next.svg'
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
  const [openDialog, setOpenDialog] = useState(false)
  const { logEvent } = useAnalytics()
  const location = useLocation()

  return (
    <div className={styles['headline-offer-banner']}>
      <div className={styles['headline-offer-text-container']}>
        <p className={styles['headline-offer-title']}>
          ✨ Nouvelle fonctionnalité : l’offre à la une !{' '}
        </p>
        <p className={styles['headline-offer-description']}>
          Votre offre à la une sera mise en avant sur votre page sur
          l’application.
        </p>
        <Button
          className={styles['headline-offer-button']}
          variant={ButtonVariant.TERNARY}
          icon={fullNextIcon}
          onClick={() => {
            setOpenDialog(true)
            logEvent(Events.CLICKED_DISCOVERED_HEADLINE_OFFER, {
              from: location.pathname,
            })
          }}
        >
          Découvrir
        </Button>
      </div>
      <img
        className={styles['headline-offer-img']}
        alt=""
        src={imgHeadlineOffer}
        role="presentation"
      />
      <Button
        className={styles['headline-offer-close-button']}
        variant={ButtonVariant.TERNARY}
        icon={strokeCloseIcon}
        aria-label="Fermer la bannière"
        onClick={close}
      />
      <HeadlineOfferInformationDialog
        onCancel={() => {
          /* istanbul ignore next */
          setOpenDialog(false)
        }}
        open={openDialog}
      />
    </div>
  )
}
