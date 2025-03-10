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
import strokeDeskIcon from 'icons/stroke-desk.svg'
import { daysOfWeek } from 'pages/VenueEdition/OpeningHoursForm/OpeningHoursForm'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'
import { BaseRadio } from 'ui-kit/form/shared/BaseRadio/BaseRadio'
import { RadioButtonWithImage } from 'ui-kit/RadioButtonWithImage/RadioButtonWithImage'

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
  const [bookingsType, setBookingsType] = useState<BookingsExportStatusFilter>()
  const [selectedDate, setSelectedDate] = useState<string | undefined>(
    priceCategoryAndScheduleCountByDate.length === 1
      ? priceCategoryAndScheduleCountByDate[0].eventDate
      : undefined
  )
  const selectedOffererId = useSelector(selectCurrentOffererId)

  const { logEvent } = useAnalytics()

  const handleSubmit = async (
    event: React.SyntheticEvent<HTMLFormElement, SubmitEvent>
  ) => {
    event.preventDefault()
    const fileFormat = event.nativeEvent.submitter?.dataset.export
    if (fileFormat === BookingExportType.CSV) {
      downloadFile(
        await api.exportBookingsForOfferAsCsv(
          offerId,
          bookingsType!,
          selectedDate!
        ),
        `reservations-${bookingsType}-${selectedDate}.csv`
      )
    } else if (fileFormat === BookingExportType.EXCEL) {
      downloadFile(
        await api.exportBookingsForOfferAsExcel(
          offerId,
          bookingsType!,
          selectedDate!
        ),
        `reservations-${bookingsType}-${selectedDate}.xlsx`
      )
    }
    logEvent(Events.CLICKED_DOWNLOAD_OFFER_BOOKINGS, {
      format: fileFormat,
      bookingStatus: bookingsType,
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
          <BaseRadio
            type="radio"
            value={eventDate}
            name="bookings-date-select"
            checked={selectedDate === eventDate}
            className={style['bookings-date-radio']}
            label={
              <div className={style['radio-label']}>
                <abbr
                  title={day}
                  className={style['bookings-day']}
                  data-testid="short-week-day"
                >
                  {day.substring(0, 3)}
                </abbr>
                <span>{format(date, FORMAT_DD_MM_YYYY)}</span>
              </div>
            }
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
      <fieldset className={style['booking-type-section']}>
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
            isChecked={bookingsType === BookingsExportStatusFilter.VALIDATED}
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

      <DialogBuilder.Footer>
        <div className={style['actions']}>
          <Dialog.Close asChild>
            <Button variant={ButtonVariant.SECONDARY}>Annuler</Button>
          </Dialog.Close>
          <Button
            variant={ButtonVariant.PRIMARY}
            type="submit"
            data-export={BookingExportType.CSV}
            disabled={selectedDate === undefined || bookingsType === undefined}
          >
            Télécharger format CSV
          </Button>
          <Button
            variant={ButtonVariant.PRIMARY}
            type="submit"
            data-export={BookingExportType.EXCEL}
            disabled={selectedDate === undefined || bookingsType === undefined}
          >
            Télécharger format Excel
          </Button>
        </div>
      </DialogBuilder.Footer>
    </form>
  )
}
