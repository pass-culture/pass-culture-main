import { ListBookingsResponseModel } from 'api/v1/gen'
import { TPreFilters } from 'core/Bookings'
import * as pcapi from 'repository/pcapi/pcapi'

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
      const bookings = await pcapi.loadFilteredBookingsRecap({
        venueId: apiFilters.offerVenueId,
        eventDate: apiFilters.offerEventDate,
        bookingPeriodBeginningDate: apiFilters.bookingBeginningDate,
        bookingPeriodEndingDate: apiFilters.bookingEndingDate,
        bookingStatusFilter: apiFilters.bookingStatusFilter,
        offerType: apiFilters.offerType,
        page: apiFilters.page,
      })

      return {
        isOk: true,
        message: null,
        payload: {
          bookings: { ...bookings, bookingsRecap: bookings.bookings_recap },
        },
      }
    } catch (e) {
      return FAILING_RESPONSE
    }
  }

export default getFilteredBookingsRecapAdapter
