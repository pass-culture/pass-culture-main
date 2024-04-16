import { api } from 'apiClient/api'
import { BookingRecapResponseModel } from 'apiClient/v1'
import {
  GetFilteredBookingsRecapAdapter,
  GetFilteredBookingsRecapAdapterPayload,
} from 'core/Bookings/types'
import { buildBookingsRecapQuery } from 'core/Bookings/utils'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

const MAX_LOADED_PAGES = 5

const FAILING_RESPONSE: AdapterFailure<GetFilteredBookingsRecapAdapterPayload> =
  {
    isOk: false,
    message: GET_DATA_ERROR_MESSAGE,
    payload: {
      bookings: [],
      pages: 0,
      currentPage: 1,
      total: 0,
    },
  }

export const getFilteredBookingsRecapAdapter: GetFilteredBookingsRecapAdapter =
  async (apiFilters) => {
    try {
      let allBookings: BookingRecapResponseModel[] = []
      let currentPage = 0
      let pages: number
      let total: number

      do {
        currentPage += 1
        const nextPageFilters = {
          ...apiFilters,
          page: currentPage,
        }
        const {
          venueId,
          offerId,
          eventDate,
          bookingPeriodBeginningDate,
          bookingPeriodEndingDate,
          bookingStatusFilter,
          offerType,
          page,
        } = buildBookingsRecapQuery(nextPageFilters)

        const bookings = await api.getBookingsPro(
          page,
          // @ts-expect-error api expect number
          venueId,
          offerId,
          eventDate,
          bookingStatusFilter,
          bookingPeriodBeginningDate,
          bookingPeriodEndingDate,
          offerType
        )
        pages = bookings.pages
        total = bookings.total

        allBookings = [...allBookings, ...bookings.bookingsRecap]
      } while (currentPage < Math.min(pages, MAX_LOADED_PAGES))

      return {
        isOk: true,
        message: null,
        payload: {
          bookings: allBookings,
          pages,
          currentPage,
          total,
        },
      }
    } catch (e) {
      return FAILING_RESPONSE
    }
  }
