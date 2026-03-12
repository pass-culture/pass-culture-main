import { yupResolver } from '@hookform/resolvers/yup'
import * as Dialog from '@radix-ui/react-dialog'
import { useForm } from 'react-hook-form'

import { api } from '@/apiClient/api'
import {
  BookingExportType,
  BookingsExportStatusFilter,
  type EventDatesInfos,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { FORMAT_DD_MM_YYYY, mapDayToFrench } from '@/commons/utils/date'
import { downloadFile } from '@/commons/utils/downloadFile'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { FieldFooter } from '@/design-system/common/FieldFooter/FieldFooter'
import { RadioButton } from '@/design-system/RadioButton/RadioButton'
import { RadioButtonGroup } from '@/design-system/RadioButtonGroup/RadioButtonGroup'
import strokeDeskIcon from '@/icons/stroke-desk.svg'
import { formatDateTime } from '@/pages/CollectiveOffer/CollectiveOfferSummary/components/CollectiveOfferSummary/components/utils/formatDatetime'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import style from './DownloadBookingsModal.module.scss'
import { validationSchema } from './validationSchema'

interface DownloadBookingsModalProps {
  offerId: number
  priceCategoryAndScheduleCountByDate: EventDatesInfos
  onCloseDialog: () => void
}

type DownloadBookingsFormValues = {
  selectedDate: string
  selectedBookingType: BookingsExportStatusFilter
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
  const selectedOffererId = useAppSelector(selectCurrentOffererId)
  const { logEvent } = useAnalytics()

  const numberOfDates = priceCategoryAndScheduleCountByDate.length

  const form = useForm<DownloadBookingsFormValues>({
    defaultValues: {
      selectedDate:
        numberOfDates === 1
          ? priceCategoryAndScheduleCountByDate[0].eventDate
          : undefined,
      selectedBookingType: BookingsExportStatusFilter.VALIDATED,
    },
    resolver: yupResolver(validationSchema),
  })

  const selectedDate = form.watch('selectedDate')

  async function onSubmit(
    data: DownloadBookingsFormValues,
    event?: React.BaseSyntheticEvent
  ) {
    const fileFormat = (event?.nativeEvent as SubmitEvent | undefined)
      ?.submitter?.dataset.export

    if (fileFormat === BookingExportType.CSV) {
      downloadFile(
        await api.exportBookingsForOfferAsCsv(
          offerId,
          data.selectedBookingType,
          data.selectedDate
        ),
        `reservations-${data.selectedBookingType}-${data.selectedDate}.csv`
      )
    } else if (fileFormat === BookingExportType.EXCEL) {
      downloadFile(
        await api.exportBookingsForOfferAsExcel(
          offerId,
          data.selectedBookingType,
          data.selectedDate
        ),
        `reservations-${data.selectedBookingType}-${data.selectedDate}.xlsx`
      )
    }

    logEvent(Events.CLICKED_DOWNLOAD_OFFER_BOOKINGS, {
      format: fileFormat,
      bookingStatus: data.selectedBookingType,
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
      <tr key={eventDate}>
        <td className={style['table-column']}>
          <RadioButton
            value={eventDate}
            name="bookings-date-select"
            checked={selectedDate === eventDate}
            hasError={!!form.formState.errors.selectedDate}
            label={`${day.substring(0, 3)} ${formatDateTime(date.toISOString(), FORMAT_DD_MM_YYYY)}`}
            onChange={() => {
              form.setValue('selectedDate', eventDate, {
                shouldValidate: true,
              })
            }}
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
    <form onSubmit={form.handleSubmit(onSubmit)} className={style['container']}>
      <fieldset className={style['date-select-section']}>
        {numberOfDates === 1 ? (
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
              {numberOfDates} {pluralizeFr(numberOfDates, 'date', 'dates')}
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
            <FieldFooter error={form.formState.errors.selectedDate?.message} />
          </>
        )}
      </fieldset>
      <RadioButtonGroup
        variant="detailed"
        label="Sélectionnez le type de réservations :"
        name="selectedBookingType"
        onChange={(e) => {
          form.setValue(
            'selectedBookingType',
            e.target.value as BookingsExportStatusFilter
          )
        }}
        checkedOption={form.watch('selectedBookingType')}
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
