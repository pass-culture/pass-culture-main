import { format } from 'date-fns'
import fullClearIcon from 'icons/full-clear.svg'
import { useState } from 'react'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import {
  BookingExportType,
  type GetIndividualOfferWithAddressResponseModel,
} from '@/apiClient/v1'
import {
  GET_BOOKINGS_QUERY_KEY,
  GET_EVENT_PRICE_CATEGORIES_AND_SCHEDULES_BY_DATE_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import {
  DEFAULT_PRE_FILTERS,
  EMPTY_FILTER_VALUE,
} from '@/commons/core/Bookings/constants'
import { FORMAT_DD_MM_YYYY, FORMAT_ISO_DATE_ONLY } from '@/commons/utils/date'
import { DEFAULT_OMNISEARCH_CRITERIA } from '@/components/Bookings/Components/Filters/constants'
import { filterBookingsRecap } from '@/components/Bookings/Components/utils/filterBookingsRecap'
import { IndividualBookingsTable } from '@/components/Bookings/IndividualBookingsTable/IndividualBookingsTable'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { DetailedModal } from '@/design-system/DetailedModal/DetailedModal'
import { formatDateTime } from '@/pages/CollectiveOffer/CollectiveOfferSummary/components/CollectiveOfferSummary/components/utils/formatDatetime'
import { getFilteredIndividualBookingsAdapter } from '@/pages/IndividualBookings/adapters/getFilteredIndividualBookingsAdapter'

import { DownloadBookingsModal } from './DownloadBookingsModal/DownloadBookingsModal'
import styles from './IndividualOfferSummaryBookingsScreen.module.scss'

interface IndividualOfferSummaryBookingsScreenProps {
  offer: GetIndividualOfferWithAddressResponseModel
}

export const IndividualOfferSummaryBookingsScreen = ({
  offer,
}: IndividualOfferSummaryBookingsScreenProps) => {
  const [bookingsStatusFilters, setBookingsStatusFilters] = useState<string[]>(
    []
  )

  const [isDownloadBookingModalOpen, setIsDownloadBookingModalOpen] =
    useState(false)

  const stockSchedulesAndPricesByDateQuery = useSWR(
    [GET_EVENT_PRICE_CATEGORIES_AND_SCHEDULES_BY_DATE_QUERY_KEY],
    () =>
      api.getOfferPriceCategoriesAndSchedulesByDates({
        path: { offer_id: offer.id },
      }),
    { fallbackData: [] }
  )

  const { data: bookings, isLoading: bookingsIsLoading } = useSWR(
    [GET_BOOKINGS_QUERY_KEY, offer.id],
    async () => {
      const { bookings } = await getFilteredIndividualBookingsAdapter(
        {
          ...DEFAULT_PRE_FILTERS,
          bookingBeginningDate: '2015-01-01',
          bookingEndingDate: format(new Date(), FORMAT_ISO_DATE_ONLY),
        },
        offer.venue.id,
        offer.id
      )
      return bookings
    },
    { fallbackData: [] }
  )

  const filteredBookings = filterBookingsRecap(bookings ?? [], {
    bookingStatus: bookingsStatusFilters,
    // TODO Improve the filtering of the base bookings page, it is a mess
    // because it mixes backend and frontend filtering in weird ways.
    // Thus I must reuse this function with lots of empty values
    // to filter by booking status
    bookingBeneficiary: EMPTY_FILTER_VALUE,
    bookingToken: EMPTY_FILTER_VALUE,
    offerISBN: EMPTY_FILTER_VALUE,
    offerName: EMPTY_FILTER_VALUE,
    selectedOmniSearchCriteria: DEFAULT_OMNISEARCH_CRITERIA,
    keywords: EMPTY_FILTER_VALUE,
    bookingInstitution: EMPTY_FILTER_VALUE,
    bookingId: EMPTY_FILTER_VALUE,
  })

  const downloadBookingsModalDescription =
    stockSchedulesAndPricesByDateQuery.data.length === 1
      ? `Date de votre évènement : ${formatDateTime(
          new Date(
            stockSchedulesAndPricesByDateQuery.data[0].eventDate
          ).toISOString(),
          FORMAT_DD_MM_YYYY
        )}`
      : 'Sélectionnez la date :'
  const downloadBookingsFormId = 'download-bookings-form'

  return (
    <>
      <div className={styles['header']}>
        <h2 className={styles['header-title']}>Réservations</h2>
        {!stockSchedulesAndPricesByDateQuery.isLoading &&
          offer.isEvent &&
          !!bookings?.length && (
            <>
              <Button
                label="Télécharger les réservations"
                onClick={() => setIsDownloadBookingModalOpen(true)}
              />
              <DetailedModal
                isOpen={isDownloadBookingModalOpen}
                onClose={() => setIsDownloadBookingModalOpen(false)}
                title="Téléchargement de vos réservations"
                description={downloadBookingsModalDescription}
                primaryAction={
                  <Button
                    type="submit"
                    form={downloadBookingsFormId}
                    data-export={BookingExportType.EXCEL}
                    label="Télécharger format Excel"
                  />
                }
                secondaryAction={
                  <Button
                    type="submit"
                    form={downloadBookingsFormId}
                    data-export={BookingExportType.CSV}
                    label="Télécharger format CSV"
                    variant={ButtonVariant.SECONDARY}
                    color={ButtonColor.NEUTRAL}
                  />
                }
                tertiaryAction={
                  <Button
                    variant={ButtonVariant.TERTIARY}
                    color={ButtonColor.NEUTRAL}
                    onClick={() => setIsDownloadBookingModalOpen(false)}
                    label="Annuler"
                    icon={fullClearIcon}
                  />
                }
                isFooterFixed
              >
                <DownloadBookingsModal
                  offerId={offer.id}
                  priceCategoryAndScheduleCountByDate={
                    stockSchedulesAndPricesByDateQuery.data
                  }
                  formId={downloadBookingsFormId}
                  onCloseDialog={() => setIsDownloadBookingModalOpen(false)}
                />
              </DetailedModal>
            </>
          )}
      </div>
      <IndividualBookingsTable
        bookings={filteredBookings}
        bookingStatuses={bookingsStatusFilters}
        updateGlobalFilters={({ bookingStatus }) => {
          setBookingsStatusFilters(bookingStatus ?? [])
        }}
        resetFilters={() => setBookingsStatusFilters([])}
        isLoading={bookingsIsLoading}
        hasNoBooking={bookings.length === 0}
      />
    </>
  )
}
