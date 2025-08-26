import { format } from 'date-fns'
import { useState } from 'react'
import useSWR from 'swr'

import { api } from '@/apiClient/api'
import type { GetIndividualOfferResponseModel } from '@/apiClient/v1'
import {
  GET_BOOKINGS_QUERY_KEY,
  GET_EVENT_PRICE_CATEGORIES_AND_SCHEDULES_BY_DATE_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { DEFAULT_PRE_FILTERS } from '@/commons/core/Bookings/constants'
import { Audience } from '@/commons/core/shared/types'
import { FORMAT_ISO_DATE_ONLY } from '@/commons/utils/date'
import { getFilteredIndividualBookingsAdapter } from '@/pages/Bookings/adapters/getFilteredIndividualBookingsAdapter'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import { BookingsTable } from '@/components/Bookings/BookingsRecapTable/BookingsTable/BookingTable'
import { ALL_BOOKING_STATUS } from '@/components/Bookings/BookingsRecapTable/Filters/constants'
import { DownloadBookingsModal } from './DownloadBookingsModal/DownloadBookingsModal'
import styles from './IndividualOfferSummaryBookingsScreen.module.scss'

interface IndividualOfferSummaryBookingsScreenProps {
  offer: GetIndividualOfferResponseModel
}

export const IndividualOfferSummaryBookingsScreen = ({
  offer,
}: IndividualOfferSummaryBookingsScreenProps) => {
  const [isDownloadBookingModalOpen, setIsDownloadBookingModalOpen] =
    useState(false)

  const stockSchedulesAndPricesByDateQuery = useSWR(
    [GET_EVENT_PRICE_CATEGORIES_AND_SCHEDULES_BY_DATE_QUERY_KEY],
    () => api.getOfferPriceCategoriesAndSchedulesByDates(offer.id),
    { fallbackData: [] }
  )

  const { data, isLoading } = useSWR([GET_BOOKINGS_QUERY_KEY], () =>
    getFilteredIndividualBookingsAdapter({
      ...DEFAULT_PRE_FILTERS,
      offerId: String(offer.id),
      bookingBeginningDate: '2015-01-01',
      bookingEndingDate: format(new Date(), FORMAT_ISO_DATE_ONLY),
    })
  )

  return (
    <>
      <div className={styles['header']}>
        <h2 className={styles['header-title']}>Réservations</h2>
        {!stockSchedulesAndPricesByDateQuery.isLoading &&
          offer.isEvent &&
          !!data?.bookings.length && (
            <DialogBuilder
              variant="drawer"
              onOpenChange={setIsDownloadBookingModalOpen}
              open={isDownloadBookingModalOpen}
              title="Téléchargement de vos réservations"
              trigger={
                <Button variant={ButtonVariant.PRIMARY}>
                  Télécharger les réservations
                </Button>
              }
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
      <BookingsTable
        key={`table-${Audience.INDIVIDUAL}`}
        audience={Audience.INDIVIDUAL}
        isLoading={isLoading}
        bookings={data?.bookings || []}
        bookingStatuses={[...ALL_BOOKING_STATUS]}
        allBookings={data?.bookings || []}
      />
    </>
  )
}
