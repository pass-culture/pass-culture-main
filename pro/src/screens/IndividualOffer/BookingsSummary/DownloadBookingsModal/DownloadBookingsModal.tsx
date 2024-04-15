import { useState } from 'react'

import { BookingsExportStatusFilter } from 'apiClient/v1'
import DialogBox from 'components/DialogBox'
import strokeDeskIcon from 'icons/stroke-desk.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import RadioButtonWithImage from 'ui-kit/RadioButtonWithImage'

import style from './DownloadBookingsModal.module.scss'

interface DownloadBookingsModalProps {
  offerId: number
  onDimiss: () => void
}

export const DownloadBookingsModal = ({
  onDimiss,
}: DownloadBookingsModalProps) => {
  const [bookingsType, setBookingsType] = useState<BookingsExportStatusFilter>()
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
            <div className={style['bookings-radio-buttons']}>
              <RadioButtonWithImage
                className={style['bookings-radio-buttons-validated']}
                name="select-bookings-type"
                icon={strokeDeskIcon}
                label="Réservations confirmées et validées uniquement"
                description="Les réservations au statut confirmées et validées ne sont plus annulables par les bénéficiaires."
                isChecked={
                  bookingsType === BookingsExportStatusFilter.VALIDATED
                }
                onChange={() =>
                  setBookingsType(BookingsExportStatusFilter.VALIDATED)
                }
                value={BookingsExportStatusFilter.VALIDATED}
              />
              <RadioButtonWithImage
                name="select-bookings-type"
                icon={strokeDeskIcon}
                label="Toutes les réservations"
                description="Les réservations dont le statut n’est pas “confirmée” ou “validée” pourront encore être annulées par les bénéficiaires."
                isChecked={bookingsType === BookingsExportStatusFilter.ALL}
                onChange={() => setBookingsType(BookingsExportStatusFilter.ALL)}
                value={BookingsExportStatusFilter.ALL}
              />
            </div>
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
