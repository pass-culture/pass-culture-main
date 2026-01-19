import * as Dialog from '@radix-ui/react-dialog'
import { useState } from 'react'

import { api } from '@/apiClient/api'
import {
  BookingExportType,
  BookingsExportStatusFilter,
  type EventDatesInfos,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { FrontendError } from '@/commons/errors/FrontendError'
import { handleUnexpectedError } from '@/commons/errors/handleUnexpectedError'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { FORMAT_DD_MM_YYYY, mapDayToFrench } from '@/commons/utils/date'
import { downloadFile } from '@/commons/utils/downloadFile'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { RadioButton } from '@/design-system/RadioButton/RadioButton'
import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import strokeDeskIcon from '@/icons/stroke-desk.svg'
import { formatDateTime } from '@/pages/CollectiveOffer/CollectiveOfferSummary/components/CollectiveOfferSummary/components/utils/formatDatetime'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import style from './DownloadBookingsModal.module.scss'

interface DownloadBookingsModalProps {
  offerId: number
  priceCategoryAndScheduleCountByDate: EventDatesInfos
  onCloseDialog: () => void
}

const daysOfWeek: string[] = [
  'monday',
  'tuesday',
  'wednesday',
  'thursday',
  'friday',
  'saturday',
  'sunday',
]

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
  const selectedOffererId = useAppSelector(selectCurrentOffererId)

  const { logEvent } = useAnalytics()

  async function handleSubmit(
    event: React.SyntheticEvent<HTMLFormElement, SubmitEvent>
  ) {
    event.preventDefault()
    const fileFormat = event.nativeEvent.submitter?.dataset.export
    if (!selectedDate) {
      return handleUnexpectedError(
        new FrontendError('`selectedDate` is undefined'),
        {
          userMessage:
            'Une erreur est survenue lors de la génération du fichier.',
        }
      )
    }

    if (fileFormat === BookingExportType.CSV) {
      downloadFile(
        await api.exportBookingsForOfferAsCsv(
          offerId,
          selectedBookingType,
          selectedDate
        ),
        `reservations-${selectedBookingType}-${selectedDate}.csv`
      )
    } else if (fileFormat === BookingExportType.EXCEL) {
      downloadFile(
        await api.exportBookingsForOfferAsExcel(
          offerId,
          selectedBookingType,
          selectedDate
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
            label={`${day.substring(0, 3)} ${formatDateTime(date.toISOString(), FORMAT_DD_MM_YYYY)}`}
            onChange={() => setSelectedDate(eventDate)}
          />
        </td>
        <td className={style['table-column']}>
          {schedulesCount} {pluralizeFr(schedulesCount, 'horaire', 'horaires')}
        </td>
        <td className={style['table-column']}>
          {priceCategoriesCount}{' '}
          {pluralizeFr(priceCategoriesCount, 'tarif', 'tarifs')}
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
            {formatDateTime(
              new Date(
                priceCategoryAndScheduleCountByDate[0].eventDate
              ).toISOString(),
              FORMAT_DD_MM_YYYY
            )}
          </h2>
        ) : (
          <>
            <legend>
              <div>Sélectionnez la date :</div>
            </legend>
            <div className={style['bookings-date-count']}>
              {priceCategoryAndScheduleCountByDate.length}
              {pluralizeFr(
                priceCategoryAndScheduleCountByDate.length,
                'date',
                'dates'
              )}
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
      <RadioButtonGroup
        variant="detailed"
        label="Sélectionnez le type de réservations :"
        name="selectedBookingType"
        onChange={(e) => {
          setSelectedBookingType(e.target.value as BookingsExportStatusFilter)
        }}
        checkedOption={selectedBookingType}
        options={[
          {
            label: 'Réservations confirmées et validées uniquement',
            value: BookingsExportStatusFilter.VALIDATED,
            description:
              'Les réservations au statut confirmées et validées ne sont plus annulables par les bénéficiaires."',
            asset: {
              variant: 'icon',
              src: strokeDeskIcon,
            },
          },
          {
            label: 'Toutes les réservations',
            value: BookingsExportStatusFilter.ALL,
            description:
              'Les réservations dont le statut n’est pas “confirmée” ou “validée” pourront encore être annulées par les bénéficiaires."',
            asset: {
              variant: 'icon',
              src: strokeDeskIcon,
            },
          },
        ]}
      />

      <DialogBuilder.Footer>
        <div className={style['actions']}>
          <Dialog.Close asChild>
            <Button
              variant={ButtonVariant.SECONDARY}
              color={ButtonColor.NEUTRAL}
              label="Annuler"
            />
          </Dialog.Close>
          <Button
            type="submit"
            data-export={BookingExportType.CSV}
            label="Télécharger format CSV"
          />

          <Button
            type="submit"
            data-export={BookingExportType.EXCEL}
            label="Télécharger format Excel"
          />
        </div>
      </DialogBuilder.Footer>
    </form>
  )
}
