import { format } from 'date-fns'
import React, { useEffect, useState } from 'react'
import useSWR from 'swr'

import { api } from 'apiClient/api'
import {
  BookingRecapResponseModel,
  GetIndividualOfferResponseModel,
} from 'apiClient/v1'
import { GET_EVENT_PRICE_CATEGORIES_AND_SCHEDULES_BY_DATE_QUERY_KEY } from 'config/swrQueryKeys'
import {
  DEFAULT_PRE_FILTERS,
  EMPTY_FILTER_VALUE,
} from 'core/Bookings/constants'
import strokeBookingHold from 'icons/stroke-booking-hold.svg'
import { getFilteredIndividualBookingsAdapter } from 'pages/Bookings/adapters/getFilteredIndividualBookingsAdapter'
import { IndividualBookingsTable } from 'screens/Bookings/BookingsRecapTable/BookingsTable/IndividualBookingsTable'
import { DEFAULT_OMNISEARCH_CRITERIA } from 'screens/Bookings/BookingsRecapTable/Filters/constants'
import { filterBookingsRecap } from 'screens/Bookings/BookingsRecapTable/utils/filterBookingsRecap'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Spinner } from 'ui-kit/Spinner/Spinner'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { FORMAT_ISO_DATE_ONLY } from 'utils/date'

import styles from './BookingsSummary.module.scss'
import { DownloadBookingsModal } from './DownloadBookingsModal/DownloadBookingsModal'

interface BookingsSummaryScreenProps {
  offer: GetIndividualOfferResponseModel
}

export const BookingsSummaryScreen = ({
  offer,
}: BookingsSummaryScreenProps) => {
  const [bookings, setBookings] = useState<BookingRecapResponseModel[] | null>(
    null
  )
  const [bookingsStatusFilters, setBookingsStatusFilter] = useState<string[]>(
    []
  )

  const stockSchedulesAndPricesByDateQuery = useSWR(
    [GET_EVENT_PRICE_CATEGORIES_AND_SCHEDULES_BY_DATE_QUERY_KEY],
    () => api.getOfferPriceCategoriesAndSchedulesByDates(offer.id),
    { fallbackData: [] }
  )

  const [isModalOpen, setIsModalOpen] = useState(false)

  useEffect(() => {
    const loadBookings = async () => {
      const response = await getFilteredIndividualBookingsAdapter({
        ...DEFAULT_PRE_FILTERS,
        offerId: String(offer.id),
        bookingBeginningDate: '2015-01-01',
        bookingEndingDate: format(new Date(), FORMAT_ISO_DATE_ONLY),
      })

      setBookings(response.bookings)
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadBookings()
  }, [setBookings, offer.id])

  if (bookings?.length === 0) {
    return (
      <div className={styles['no-data']}>
        <SvgIcon
          className={styles['no-data-icon']}
          src={strokeBookingHold}
          alt=""
          width="128"
        />

        <div>Vous n’avez pas encore de réservations</div>
      </div>
    )
  }

  const filteredBookings = filterBookingsRecap(bookings ?? [], {
    bookingStatus: bookingsStatusFilters,
    // Improve the filtering of the base bookings page, it is a mess
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
      {isModalOpen && (
        <DownloadBookingsModal
          offerId={offer.id}
          priceCategoryAndScheduleCountByDate={
            stockSchedulesAndPricesByDateQuery.data
          }
          onDimiss={() => setIsModalOpen(false)}
        />
      )}

      <div className={styles['header']}>
        <h2 className={styles['header-title']}>Réservations</h2>
        {!stockSchedulesAndPricesByDateQuery.isLoading &&
          offer.isEvent &&
          bookings !== null &&
          bookings.length && (
            <Button
              variant={ButtonVariant.PRIMARY}
              onClick={() => setIsModalOpen(true)}
            >
              Télécharger les réservations
            </Button>
          )}
      </div>
      {bookings !== null ? (
        <IndividualBookingsTable
          bookings={filteredBookings}
          bookingStatuses={bookingsStatusFilters}
          updateGlobalFilters={({ bookingStatus }) => {
            setBookingsStatusFilter(bookingStatus ?? [])
          }}
          resetFilters={() => setBookingsStatusFilter([])}
        />
      ) : (
        <Spinner />
      )}
    </>
  )
}
