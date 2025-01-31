import * as RadixDialog from '@radix-ui/react-dialog'

import fullThreeDotsIcon from 'icons/full-three-dots.svg'
import { Button } from 'ui-kit/Button/Button'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './HeadlineOfferInformationDialog.module.scss'
import placeholderVideo from './placeholder-video-delete-me-soon.png'

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
          {/* // TODO feature implement explicative video here */}
          <img
            src={placeholderVideo}
            alt=""
            className={styles['placeholder-video']}
            role="presentation"
          />
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
          Bien noté
        </Button>
      </div>
    </DialogBuilder>
  )
}
