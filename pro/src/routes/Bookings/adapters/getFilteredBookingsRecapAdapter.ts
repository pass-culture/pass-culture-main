import { apiV1 as api } from 'api/api'
import { BookingRecapResponseModel } from 'api/openapi_generator/v1/gen'
import {
  GetFilteredBookingsRecapAdapter,
  GetFilteredBookingsRecapAdapterPayload,
} from 'core/Bookings'

import { buildBookingsRecapQuery } from './utils'

const MAX_LOADED_PAGES = 5

const FAILING_RESPONSE: AdapterFailure<GetFilteredBookingsRecapAdapterPayload> =
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

export const getFilteredBookingsRecapAdapter: GetFilteredBookingsRecapAdapter =
  async apiFilters => {
    try {
      let allBookings: BookingRecapResponseModel[] = []
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
          offerType,
          page,
        } = buildBookingsRecapQuery(nextPageFilters)

        const bookings = await api.getBookingsGetBookingsPro(
          page,
          // @ts-expect-error api expect number
          venueId,
          eventDate,
          bookingStatusFilter,
          bookingPeriodBeginningDate,
          bookingPeriodEndingDate,
          offerType
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

export default getFilteredBookingsRecapAdapter
