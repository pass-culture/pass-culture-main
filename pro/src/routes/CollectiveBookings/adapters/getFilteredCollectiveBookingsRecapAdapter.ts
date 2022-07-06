import {
  GetFilteredCollectiveBookingsRecapAdapter,
  GetFilteredCollectiveBookingsRecapAdapterPayload,
} from 'core/Bookings'

import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { api } from 'apiClient/api'
import { buildBookingsRecapQuery } from 'core/Bookings/utils'

const MAX_LOADED_PAGES = 5

const FAILING_RESPONSE: AdapterFailure<GetFilteredCollectiveBookingsRecapAdapterPayload> =
  {
    isOk: false,
    message: GET_DATA_ERROR_MESSAGE,
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
