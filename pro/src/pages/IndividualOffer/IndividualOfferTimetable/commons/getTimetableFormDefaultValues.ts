import type {
  GetIndividualOfferWithAddressResponseModel,
  GetOfferStockResponseModel,
  WeekdayOpeningHoursTimespans,
} from '@/apiClient/v1'

import { areOpeningHoursEmpty } from './areOpeningHoursEmpty'
import type { IndividualOfferTimetableFormValues } from './types'

export function getTimetableFormDefaultValues({
  openingHours,
  stocks,
  offer,
}: {
  openingHours?: WeekdayOpeningHoursTimespans | null
  stocks?: GetOfferStockResponseModel[]
  offer: GetIndividualOfferWithAddressResponseModel
}) {
  const openingHoursEmpty = areOpeningHoursEmpty(openingHours)

  return {
    timetableType: openingHoursEmpty ? 'calendar' : 'openingHours',
    openingHours: openingHours,
    hasStartDate: 'no', //  TODO : retrieve the openingHours startDate when it exists on the model
    hasEndDate: 'no', //  TODO : retrieve the openingHours endDate when it exists on the model
    startDate: undefined, //  TODO : retrieve the openingHours startDate when it exists on the model
    endDate: undefined, //  TODO : retrieve the openingHours endDate when it exists on the model
    quantityPerPriceCategories:
      !openingHoursEmpty && stocks && stocks.length > 0
        ? stocks.map((stock) => ({
            priceCategory: stock.priceCategoryId?.toString() || '',
            quantity: stock.quantity,
          }))
        : [{ priceCategory: offer.priceCategories?.[0].id.toString() || '' }],
  } satisfies IndividualOfferTimetableFormValues
}
