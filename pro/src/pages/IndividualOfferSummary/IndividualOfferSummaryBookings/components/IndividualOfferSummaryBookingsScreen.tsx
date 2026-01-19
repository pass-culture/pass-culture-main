import { format } from 'date-fns'
import { useState } from 'react'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import type { GetIndividualOfferResponseModel } from '@/apiClient/v1'
import {
  GET_BOOKINGS_QUERY_KEY,
  GET_EVENT_PRICE_CATEGORIES_AND_SCHEDULES_BY_DATE_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import {
  DEFAULT_PRE_FILTERS,
  EMPTY_FILTER_VALUE,
} from '@/commons/core/Bookings/constants'
import { FORMAT_ISO_DATE_ONLY } from '@/commons/utils/date'
import { DEFAULT_OMNISEARCH_CRITERIA } from '@/components/Bookings/Components/Filters/constants'
import { filterBookingsRecap } from '@/components/Bookings/Components/utils/filterBookingsRecap'
import { IndividualBookingsTable } from '@/components/Bookings/IndividualBookingsTable/IndividualBookingsTable'
import { Button } from '@/design-system/Button/Button'
import { getFilteredIndividualBookingsAdapter } from '@/pages/Bookings/adapters/getFilteredIndividualBookingsAdapter'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import { DownloadBookingsModal } from './DownloadBookingsModal/DownloadBookingsModal'
import styles from './IndividualOfferSummaryBookingsScreen.module.scss'

interface IndividualOfferSummaryBookingsScreenProps {
  offer: GetIndividualOfferResponseModel
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
    () => api.getOfferPriceCategoriesAndSchedulesByDates(offer.id),
    { fallbackData: [] }
  )

  const { data: bookings, isLoading: bookingsIsLoading } = useSWR(
    [GET_BOOKINGS_QUERY_KEY],
    async () => {
      const { bookings } = await getFilteredIndividualBookingsAdapter({
        ...DEFAULT_PRE_FILTERS,
        offerId: String(offer.id),
        bookingBeginningDate: '2015-01-01',
        bookingEndingDate: format(new Date(), FORMAT_ISO_DATE_ONLY),
      })
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

  return (
    <>
      <div className={styles['header']}>
        <h2 className={styles['header-title']}>Réservations</h2>
        {!stockSchedulesAndPricesByDateQuery.isLoading &&
          offer.isEvent &&
          !!bookings?.length && (
            <DialogBuilder
              variant="drawer"
              onOpenChange={setIsDownloadBookingModalOpen}
              open={isDownloadBookingModalOpen}
              title="Téléchargement de vos réservations"
              trigger={<Button label="Télécharger les réservations" />}
            >
              <DownloadBookingsModal
                offerId={offer.id}
                priceCategoryAndScheduleCountByDate={
                  stockSchedulesAndPricesByDateQuery.data
                }
                onCloseDialog={() => setIsDownloadBookingModalOpen(false)}
              />
            </DialogBuilder>
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
