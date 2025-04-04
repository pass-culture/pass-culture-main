import * as RadixDialog from '@radix-ui/react-dialog'
import { useLocation } from 'react-router-dom'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import fullNextIcon from 'icons/full-next.svg'
import fullThreeDotsIcon from 'icons/full-three-dots.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import imagePopinDiscover from './discover-popin.png'
import styles from './HeadlineOfferInformationDialog.module.scss'

type HeadlineOfferInformationDialogProps = {
  triggerClassName: string
}

export const HeadlineOfferInformationDialog = ({
  triggerClassName,
}: HeadlineOfferInformationDialogProps) => {
  const { logEvent } = useAnalytics()
  const location = useLocation()

  return (
    <DialogBuilder
      trigger={
        <Button
          className={triggerClassName}
          iconClassName={styles['button-icon']}
          variant={ButtonVariant.TERNARY}
          icon={fullNextIcon}
          onClick={() => {
            logEvent(Events.CLICKED_DISCOVERED_HEADLINE_OFFER, {
              from: location.pathname,
            })
          }}
        >
          Découvrir
        </Button>
      }
    >
      <div className={styles['dialog']}>
        <img
          src={imagePopinDiscover}
          alt=""
          className={styles['image']}
          role="presentation"
        />

        <RadixDialog.Title className={styles['dialog-title']}>
          <span aria-hidden="true">✨</span> Nouvelle fonctionnalité : la mise à
          la une !
        </RadixDialog.Title>

        <div className={styles['dialog-content']}>
          <p className={styles['informations-title']}>Comment faire ?</p>
          <ul className={styles['informations']}>
            <li>
              <span className={styles['information-option']}>
                Ouvrez le menu option{' '}
                <SvgIcon
                  className={styles['options-icon']}
                  src={fullThreeDotsIcon}
                  alt={''}
                  width="20"
                />{' '}
                au bout de la ligne de votre offre.
              </span>
            </li>
            <li>Cliquez sur le bouton “Mettre à la une”.</li>
          </ul>
          <p>
            Votre offre sera mise en avant sur votre page partenaire de
            l’application !
          </p>
        </div>

        <RadixDialog.Close asChild>
          <Button className={styles['dialog-button']}>Bien noté</Button>
        </RadixDialog.Close>
      </div>
    </DialogBuilder>
  )
}
