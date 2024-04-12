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
      labelledBy="download-bookings-modal"
      onDismiss={onDimiss}
    >
      <form>
        <div className={style['container']}>
          <h1 id="download-bookings-modal" className={style['header']}>
            Télécharger vos réservations
          </h1>
          <fieldset>
            <legend>
              <div>Sélectionner la date:</div>
            </legend>
          </fieldset>
          <fieldset>
            <legend>
              <div>Sélectionnez le type de réservations :</div>
            </legend>
          </fieldset>

          <div className={style['actions']}>
            <Button variant={ButtonVariant.SECONDARY} onClick={onDimiss}>
              Annuler
            </Button>
            <Button variant={ButtonVariant.PRIMARY} type="submit" value="csv">
              Télécharger au format CSV
            </Button>
            <Button variant={ButtonVariant.PRIMARY} type="submit" value="xlsx">
              Télécharger au format Excel
            </Button>
          </div>
        </div>
      </form>
    </DialogBox>
  )
}
