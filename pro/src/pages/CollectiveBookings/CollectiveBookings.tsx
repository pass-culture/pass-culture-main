import { useLocation } from 'react-router'

import { api } from '@/apiClient/api'
import { CollectiveBookingResponseModel } from '@/apiClient/v1'
import { Layout } from '@/app/App/layout/Layout'
import { PreFiltersParams } from '@/commons/core/Bookings/types'
import { buildBookingsRecapQuery } from '@/commons/core/Bookings/utils'
import { Audience } from '@/commons/core/shared/types'
import { BookingsContainer } from '@/components/Bookings/Bookings'

const MAX_LOADED_PAGES = 5

const CollectiveBookings = (): JSX.Element => {
  const location = useLocation()

  const getUserHasCollectiveBookingsAdapter = async () => {
    const { hasBookings } = await api.getUserHasCollectiveBookings()

    return hasBookings
  }

  const getFilteredCollectiveBookingsAdapter = async (
    apiFilters: PreFiltersParams & { page?: number }
  ) => {
    let allBookings: CollectiveBookingResponseModel[] = []
    let currentPage = 0
    let pages: number

    do {
      currentPage += 1
      const nextPageFilters = {
        ...apiFilters,
        page: currentPage,
      }
      const {
        venueId,
        eventDate,
        bookingPeriodBeginningDate,
        bookingPeriodEndingDate,
        bookingStatusFilter,
        page,
      } = buildBookingsRecapQuery(nextPageFilters)

      const bookings = await api.getCollectiveBookingsPro(
        page,
        // @ts-expect-error type string is not assignable to type number
        venueId,
        eventDate,
        bookingStatusFilter,
        bookingPeriodBeginningDate,
        bookingPeriodEndingDate
      )
      pages = bookings.pages

      allBookings = [...allBookings, ...bookings.bookingsRecap]
    } while (currentPage < Math.min(pages, MAX_LOADED_PAGES))

    return {
      bookings: allBookings,
      pages,
      currentPage,
    }
  }

  return (
    <Layout mainHeading="Réservations collectives">
      <BookingsContainer
        audience={Audience.COLLECTIVE}
        getFilteredBookingsAdapter={getFilteredCollectiveBookingsAdapter}
        getUserHasBookingsAdapter={getUserHasCollectiveBookingsAdapter}
        locationState={location.state}
      />
    </Layout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = CollectiveBookings
