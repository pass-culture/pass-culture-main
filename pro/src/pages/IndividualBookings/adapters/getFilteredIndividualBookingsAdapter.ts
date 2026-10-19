import { api } from '@/apiClient/api'
import type {
  BookingRecapResponseModel,
  GetBookingsProResponseModel,
} from '@/apiClient/v1'
import type { PreFiltersParams } from '@/commons/core/Bookings/types'
import { buildBookingsRecapQuery } from '@/commons/core/Bookings/utils'

const MAX_LOADED_PAGES = 10

export const getFilteredIndividualBookingsAdapter = async (
  apiFilters: PreFiltersParams & {
    page?: number
  },
  venueId: number,
  offerId?: number
) => {
  const allBookingsPromises: Promise<GetBookingsProResponseModel>[] = []
  const {
    page = 1,
    eventDate,
    bookingStatusFilter,
    bookingPeriodBeginningDate,
    bookingPeriodEndingDate,
    offererAddressId,
  } = buildBookingsRecapQuery(apiFilters)

  const firstPageResponse = await api.getBookingsPro({
    query: {
      venueId,
      page,
      offerId,
      eventDate,
      bookingStatusFilter,
      bookingPeriodBeginningDate,
      bookingPeriodEndingDate,
      offererAddressId,
    },
  })
  let currentPage = firstPageResponse.page
  const pages = firstPageResponse.pages

  while (currentPage < Math.min(pages, MAX_LOADED_PAGES)) {
    currentPage += 1
    const nextPageFilters = {
      ...apiFilters,
      page: currentPage,
    }
    const {
      page = 1,
      eventDate,
      bookingStatusFilter,
      bookingPeriodBeginningDate,
      bookingPeriodEndingDate,
      offererAddressId,
    } = buildBookingsRecapQuery(nextPageFilters)

    allBookingsPromises.push(
      api.getBookingsPro({
        query: {
          venueId,
          page,
          offerId,
          eventDate,
          bookingStatusFilter,
          bookingPeriodBeginningDate,
          bookingPeriodEndingDate,
          offererAddressId,
        },
      })
    )
  }

  const promisesResult: BookingRecapResponseModel[] = (
    await Promise.all(allBookingsPromises)
  ).reduce((acc: BookingRecapResponseModel[], response) => {
    acc.push(...response.bookingsRecap)
    return acc
  }, [])

  return {
    bookings: [...firstPageResponse.bookingsRecap, ...promisesResult],
    pages,
    currentPage,
  }
}
