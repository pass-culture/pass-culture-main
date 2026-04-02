import { format } from 'date-fns'
import { useState } from 'react'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import {
  type BookingRecapStatus,
  type BookingSortableColumn,
  type GetIndividualOfferResponseModel,
  SortOrder,
} from '@/apiClient/v1'
import {
  GET_BOOKINGS_QUERY_KEY,
  GET_EVENT_PRICE_CATEGORIES_AND_SCHEDULES_BY_DATE_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { DEFAULT_PRE_FILTERS } from '@/commons/core/Bookings/constants'
import { SortingMode } from '@/commons/hooks/useColumnSorting'
import { FORMAT_ISO_DATE_ONLY } from '@/commons/utils/date'
import { IndividualBookingsTable } from '@/components/Bookings/IndividualBookingsTable/IndividualBookingsTable'
import { Button } from '@/design-system/Button/Button'
import { getFilteredIndividualBookingsAdapter } from '@/pages/IndividualBookings/adapters/getFilteredIndividualBookingsAdapter'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import { DownloadBookingsModal } from './DownloadBookingsModal/DownloadBookingsModal'
import styles from './IndividualOfferSummaryBookingsScreen.module.scss'

interface IndividualOfferSummaryBookingsScreenProps {
  offer: GetIndividualOfferResponseModel
}

export const IndividualOfferSummaryBookingsScreen = ({
  offer,
}: IndividualOfferSummaryBookingsScreenProps) => {
  const [bookingsStatusFilters, setBookingsStatusFilters] = useState<
    BookingRecapStatus[]
  >([])
  const [page, setPage] = useState(1)
  const [sortBy, setSortBy] = useState<BookingSortableColumn | undefined>()
  const [sortOrder, setSortOrder] = useState<SortOrder | undefined>()

  const [isDownloadBookingModalOpen, setIsDownloadBookingModalOpen] =
    useState(false)

  const stockSchedulesAndPricesByDateQuery = useSWR(
    [GET_EVENT_PRICE_CATEGORIES_AND_SCHEDULES_BY_DATE_QUERY_KEY],
    () => api.getOfferPriceCategoriesAndSchedulesByDates(offer.id),
    { fallbackData: [] }
  )

  const handleSortChange = (column: string | null, order: SortingMode) => {
    setPage(1)
    setSortBy(column ? (column as BookingSortableColumn) : undefined)
    setSortOrder(
      order === SortingMode.ASC
        ? SortOrder.ASC
        : order === SortingMode.DESC
          ? SortOrder.DESC
          : undefined
    )
  }

  const { data: bookingsResult, isLoading: bookingsIsLoading } = useSWR(
    [
      GET_BOOKINGS_QUERY_KEY,
      offer.id,
      page,
      sortBy,
      sortOrder,
      bookingsStatusFilters,
    ],
    async () => {
      return await getFilteredIndividualBookingsAdapter({
        ...DEFAULT_PRE_FILTERS,
        offerId: String(offer.id),
        bookingBeginningDate: '2015-01-01',
        bookingEndingDate: format(new Date(), FORMAT_ISO_DATE_ONLY),
        page,
        sortBy,
        sortOrder,
        bookingStatus:
          bookingsStatusFilters.length > 0 ? bookingsStatusFilters : undefined,
      })
    },
    {
      fallbackData: { bookings: [], pages: 0, total: 0, currentPage: 1 },
    }
  )

  return (
    <>
      <div className={styles['header']}>
        <h2 className={styles['header-title']}>Réservations</h2>
        {!stockSchedulesAndPricesByDateQuery.isLoading &&
          offer.isEvent &&
          !!bookingsResult.total && (
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
        bookings={bookingsResult.bookings}
        bookingStatuses={bookingsStatusFilters}
        updateGlobalFilters={({ bookingStatus }) => {
          setPage(1)
          setBookingsStatusFilters(
            (bookingStatus ?? []) as BookingRecapStatus[]
          )
        }}
        resetFilters={() => {
          setPage(1)
          setBookingsStatusFilters([])
        }}
        isLoading={bookingsIsLoading}
        hasNoBooking={bookingsResult.total === 0}
        currentPage={page}
        pageCount={bookingsResult.pages}
        onPageChange={setPage}
        onSortChange={handleSortChange}
      />
    </>
  )
}
