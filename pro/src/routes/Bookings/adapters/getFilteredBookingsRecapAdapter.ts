import { api } from 'api/v1/api'
import { ListBookingsResponseModel } from 'api/v1/gen'
import { TPreFilters } from 'core/Bookings'

import { buildBookingsRecapQuery } from './utils'

type IPayload = {
  bookings: ListBookingsResponseModel
}

type GetFilteredBookingsRecapAdapter = Adapter<
  TPreFilters & { page?: number },
  IPayload,
  IPayload
>

const FAILING_RESPONSE: AdapterFailure<IPayload> = {
  isOk: false,
  message: 'Nous avons rencontré un problème lors du chargemement des données',
  payload: {
    bookings: {
      page: 0,
      pages: 0,
      bookingsRecap: [],
      total: 0,
    },
  },
}

export const getFilteredBookingsRecapAdapter: GetFilteredBookingsRecapAdapter =
  async apiFilters => {
    try {
      const {
        venueId,
        eventDate,
        bookingPeriodBeginningDate,
        bookingPeriodEndingDate,
        bookingStatusFilter,
        offerType,
        page,
      } = buildBookingsRecapQuery(apiFilters)
      const bookings = await api.getBookingsGetBookingsPro(
        page,
        // @ts-expect-error vgfk
        venueId,
        eventDate,
        bookingStatusFilter,
        bookingPeriodBeginningDate,
        bookingPeriodEndingDate,
        offerType
      )

      return {
        isOk: true,
        message: null,
        payload: {
          bookings,
        },
      }
    } catch (e) {
      return FAILING_RESPONSE
    }
  }

export default getFilteredBookingsRecapAdapter
