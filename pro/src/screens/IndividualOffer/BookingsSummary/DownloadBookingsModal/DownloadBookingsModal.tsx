import DialogBox from 'components/DialogBox'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import style from './DownloadBookingsModal.module.scss'

interface DownloadBookingsModalProps {
  offerId: number
  onDimiss: () => void
}

export const DownloadBookingsModal = ({
  onDimiss,
}: DownloadBookingsModalProps) => {
  return (
    <DialogBox
      hasCloseButton
      labelledBy="Télécharger vos réservations"
      onDismiss={onDimiss}
    >
      <div className={style['container']}>
        <header>
          <h3 className={style['header']}>Télécharger vos réservations</h3>
        </header>
        <ol>
          <div className={style['section']}>
            <h3 className={style['section-title']}>
              <li>
                Sélectionner la date dont vous souhaitez télécharger les
                réservations :
              </li>
            </h3>
          </div>
          <div className={style['section']}>
            <h3 className={style['section-title']}>
              <li>
                Sélectionner le type de réservations que vous souhaitez
                télécharger :
              </li>
            </h3>
          </div>
        </ol>
        <div className={style['actions']}>
          <Button variant={ButtonVariant.SECONDARY} onClick={onDimiss}>
            Annuler
          </Button>
          <Button variant={ButtonVariant.PRIMARY}>Format CSV (.csv)</Button>
          <Button variant={ButtonVariant.PRIMARY}>Format Excel (.xslx)</Button>
        </div>
      </div>
    </DialogBox>
  )
}
