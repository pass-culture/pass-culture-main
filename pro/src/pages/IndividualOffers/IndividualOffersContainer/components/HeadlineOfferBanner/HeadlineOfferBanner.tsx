import { useGTMHeadlineOfferAbTest } from 'commons/hooks/useGTMHeadlineOfferAbTest'
import strokeCloseIcon from 'icons/stroke-close.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Callout } from 'ui-kit/Callout/Callout'

import imgHeadlineOffer from './assets/headlineOffer.png'
import { HeadlineOfferInformationDialog } from './components/HeadlineOfferInformationDialog'
import styles from './HeadlineOfferBanner.module.scss'

type HeadlineOfferBannerProps = {
  close: () => void
}

export const HeadlineOfferBanner = ({ close }: HeadlineOfferBannerProps) => {
  const isInAbTest = useGTMHeadlineOfferAbTest()

  return (
    <>
      {isInAbTest ? (
        <div
          className={styles['headline-offer-banner']}
          data-testid="awesome-banner"
        >
          <div className={styles['headline-offer-text-container']}>
            <p className={styles['headline-offer-title']}>
              <span aria-hidden="true">✨</span> Nouvelle fonctionnalité :
              l’offre à la une !{' '}
            </p>
            <p className={styles['headline-offer-description']}>
              Votre offre à la une sera mise en avant sur votre page sur
              l’application.
            </p>
            <HeadlineOfferInformationDialog
              triggerClassName={styles['headline-offer-button']}
            />
          </div>
          <img
            className={styles['headline-offer-img']}
            alt=""
            src={imgHeadlineOffer}
            role="presentation"
          />
          <div>
            <Button
              className={styles['headline-offer-button']}
              variant={ButtonVariant.TERNARY}
              icon={strokeCloseIcon}
              iconAlt="Fermer la bannière"
              onClick={close}
            />
          </div>
        </div>
      ) : (
        <Callout
          title="Nouvelle fonctionnalité : l’offre à la une !"
          closable
          onClose={close}
          className={styles['headline-offer-callout']}
          testId="regular-banner"
        >
          Votre offre à la une sera mise en avant sur votre page sur
          l’application.
          <HeadlineOfferInformationDialog
            triggerClassName={styles['headline-offer-callout-discover-button']}
          />
        </Callout>
      )}
    </>
  )
}
