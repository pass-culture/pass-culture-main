import * as pcapi from 'repository/pcapi/pcapi'

import {
  CollectiveBookingResponseModel,
  GetFilteredCollectiveBookingsRecapAdapter,
  GetFilteredCollectiveBookingsRecapAdapterPayload,
} from 'core/Bookings'

import { buildBookingsRecapQuery } from 'core/Bookings/utils'

const MAX_LOADED_PAGES = 5

const FAILING_RESPONSE: AdapterFailure<GetFilteredCollectiveBookingsRecapAdapterPayload> =
  {
    isOk: false,
    message:
      'Nous avons rencontré un problème lors du chargemement des données',
    payload: {
      bookings: [],
      pages: 0,
      currentPage: 1,
    },
  }

export const getFilteredCollectiveBookingsRecapAdapter: GetFilteredCollectiveBookingsRecapAdapter =
  async apiFilters => {
    try {
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

        const bookings = await pcapi.getCollectiveBookings(
          page,
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
        isOk: true,
        message: null,
        payload: {
          bookings: allBookings,
          pages,
          currentPage,
        },
      }
    } catch (e) {
      return FAILING_RESPONSE
    }
  }

export default getFilteredCollectiveBookingsRecapAdapter
