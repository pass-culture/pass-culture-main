import * as RadixDialog from '@radix-ui/react-dialog'

import fullThreeDotsIcon from 'icons/full-three-dots.svg'
import { Button } from 'ui-kit/Button/Button'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './HeadlineOfferInformationDialog.module.scss'

type HeadlineOfferInformationDialogProps = {
  onCancel: () => void
  open: boolean
}

export const HeadlineOfferInformationDialog = ({
  onCancel,
  open,
}: HeadlineOfferInformationDialogProps) => {
  return (
    <DialogBuilder
      open={open}
      /* istanbul ignore next */
      onOpenChange={(open) => !open && onCancel()}
    >
      <div className={styles['dialog']}>
        <div className={styles['video-container']}>
          <iframe
            width="393"
            height="228"
            className={styles['video']}
            src="https://www.youtube.com/embed/Tg8ETHWG_Zc"
            title="Vidéo comment mettre une offre à la une"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
            referrerPolicy="strict-origin-when-cross-origin"
          ></iframe>
        </div>

        <RadixDialog.Title className={styles['dialog-title']}>
          ✨ Nouvelle fonctionnalité : la mise à la une !
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

        <Button className={styles['dialog-button']} onClick={onCancel}>
          J’ai compris
        </Button>
      </div>
    </DialogBuilder>
  )
}
