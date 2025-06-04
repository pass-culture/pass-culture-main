import * as Dialog from '@radix-ui/react-dialog'
import { format } from 'date-fns'
import { useState } from 'react'
import { useSelector } from 'react-redux'

import { api } from 'apiClient/api'
import {
  BookingExportType,
  BookingsExportStatusFilter,
  EventDatesInfos,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { FORMAT_DD_MM_YYYY, mapDayToFrench } from 'commons/utils/date'
import { downloadFile } from 'commons/utils/downloadFile'
import { pluralize } from 'commons/utils/pluralize'
import { RadioButton } from 'design-system/RadioButton/RadioButton'
import strokeDeskIcon from 'icons/stroke-desk.svg'
import { daysOfWeek } from 'pages/VenueEdition/OpeningHoursForm/OpeningHoursForm'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { RadioGroup } from 'ui-kit/formV2/RadioGroup/RadioGroup'

import style from './DownloadBookingsModal.module.scss'

interface DownloadBookingsModalProps {
  offerId: number
  priceCategoryAndScheduleCountByDate: EventDatesInfos
  onCloseDialog: () => void
}

export const DownloadBookingsModal = ({
  offerId,
  priceCategoryAndScheduleCountByDate,
  onCloseDialog,
}: DownloadBookingsModalProps) => {
  const [selectedBookingType, setSelectedBookingType] =
    useState<BookingsExportStatusFilter>(BookingsExportStatusFilter.VALIDATED)
  const [selectedDate, setSelectedDate] = useState<string | undefined>(
    priceCategoryAndScheduleCountByDate.length === 1
      ? priceCategoryAndScheduleCountByDate[0].eventDate
      : undefined
  )
  const selectedOffererId = useSelector(selectCurrentOffererId)

  const { logEvent } = useAnalytics()

  async function handleSubmit(
    event: React.SyntheticEvent<HTMLFormElement, SubmitEvent>
  ) {
    event.preventDefault()
    const fileFormat = event.nativeEvent.submitter?.dataset.export
    if (fileFormat === BookingExportType.CSV) {
      downloadFile(
        await api.exportBookingsForOfferAsCsv(
          offerId,
          selectedBookingType!,
          selectedDate!
        ),
        `reservations-${selectedBookingType}-${selectedDate}.csv`
      )
    } else if (fileFormat === BookingExportType.EXCEL) {
      downloadFile(
        await api.exportBookingsForOfferAsExcel(
          offerId,
          selectedBookingType!,
          selectedDate!
        ),
        `reservations-${selectedBookingType}-${selectedDate}.xlsx`
      )
    }
    logEvent(Events.CLICKED_DOWNLOAD_OFFER_BOOKINGS, {
      format: fileFormat,
      bookingStatus: selectedBookingType,
      offerId,
      offerType: 'individual',
      offererId: selectedOffererId?.toString(),
    })

    onCloseDialog()
  }

  const createDateRow = (
    eventDate: string,
    schedulesCount: number,
    priceCategoriesCount: number
  ) => {
    const date = new Date(eventDate)
    const day = mapDayToFrench(daysOfWeek[(date.getDay() + 6) % 7])
    return (
      <tr key={eventDate} className={style['table-row']}>
        <td className={style['table-column']}>
          <RadioButton
            value={eventDate}
            name="bookings-date-select"
            checked={selectedDate === eventDate}
            label={`${day.substring(0, 3)} ${format(date, FORMAT_DD_MM_YYYY)}`}
            onChange={() => setSelectedDate(eventDate)}
          />
        </td>
        <td className={style['table-column']}>
          {pluralize(schedulesCount, 'horaire')}
        </td>
        <td className={style['table-column']}>
          {pluralize(priceCategoriesCount, 'tarif')}
        </td>
      </tr>
    )
  }

  return (
    <form onSubmit={handleSubmit} className={style['container']}>
      <fieldset className={style['date-select-section']}>
        {priceCategoryAndScheduleCountByDate.length === 1 ? (
          <h2 className={style['one-booking-date-section']}>
            Date de votre évènement :{' '}
            {format(
              new Date(priceCategoryAndScheduleCountByDate[0].eventDate),
              FORMAT_DD_MM_YYYY
            )}
          </h2>
        ) : (
          <>
            <legend>
              <div>Sélectionnez la date :</div>
            </legend>
            <div className={style['bookings-date-count']}>
              {pluralize(priceCategoryAndScheduleCountByDate.length, 'date')}
            </div>
            <hr className={style['horizontal-line']} />
            <table className={style['date-select-table']}>
              <thead className={style['date-select-table-header']}>
                <tr>
                  <th scope="col" className={style['table-header']}>
                    Date
                  </th>
                  <th className={style['table-header']} scope="col">
                    Horaires
                  </th>
                  <th className={style['table-header']} scope="col">
                    Tarifs
                  </th>
                </tr>
              </thead>
              <tbody>
                {priceCategoryAndScheduleCountByDate.map((date) =>
                  createDateRow(
                    date.eventDate,
                    date.scheduleCount,
                    date.priceCategoriesCount
                  )
                )}
              </tbody>
            </table>
            <hr className={style['horizontal-line']} />
          </>
        )}
      </fieldset>
      <RadioGroup
        variant="detailed"
        legend="Sélectionnez le type de réservations :"
        name="selectedBookingType"
        onChange={(e) => {
          setSelectedBookingType(e.target.value as BookingsExportStatusFilter)
        }}
        checkedOption={selectedBookingType}
        group={[
          {
            label: 'Réservations confirmées et validées uniquement',
            value: BookingsExportStatusFilter.VALIDATED,
            description:
              'Les réservations au statut confirmées et validées ne sont plus annulables par les bénéficiaires."',
            icon: strokeDeskIcon,
          },
          {
            label: 'Toutes les réservations',
            value: BookingsExportStatusFilter.ALL,
            description:
              'Les réservations dont le statut n’est pas “confirmée” ou “validée” pourront encore être annulées par les bénéficiaires."',
            icon: strokeDeskIcon,
          },
        ]}
      />

      <DialogBuilder.Footer>
        <div className={style['actions']}>
          <Dialog.Close asChild>
            <Button variant={ButtonVariant.SECONDARY}>Annuler</Button>
          </Dialog.Close>
          <Button
            variant={ButtonVariant.PRIMARY}
            type="submit"
            data-export={BookingExportType.CSV}
          >
            Télécharger format CSV
          </Button>
          <Button
            variant={ButtonVariant.PRIMARY}
            type="submit"
            data-export={BookingExportType.EXCEL}
          >
            Télécharger format Excel
          </Button>
        </div>
      </DialogBuilder.Footer>
    </form>
  )
}
