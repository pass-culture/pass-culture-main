import type {
  GetIndividualOfferWithAddressResponseModel,
  GetOfferStockResponseModel,
  WeekdayOpeningHoursTimespans,
} from '@/apiClient/v1'

import { areOpeningHoursEmpty } from './areOpeningHoursEmpty'
import { getTimetableDefaultOpeningHours } from './getTimetableDefaultOpeningHours'
import { HasDateEnum, type IndividualOfferTimetableFormValues } from './types'

export function getTimetableFormDefaultValues({
  openingHours,
  venueOpeningHours,
  stocks,
  offer,
  isOhoFFEnabled,
}: {
  openingHours?: WeekdayOpeningHoursTimespans | null
  venueOpeningHours?: WeekdayOpeningHoursTimespans | null
  stocks?: GetOfferStockResponseModel[]
  offer: GetIndividualOfferWithAddressResponseModel
  isOhoFFEnabled: boolean
}) {
  const prefilledOpeningHours = getTimetableDefaultOpeningHours({
    offerOpeningHours: openingHours,
    venueOpeningHours: venueOpeningHours,
  })

  return {
    timetableType:
      !isOhoFFEnabled || areOpeningHoursEmpty(openingHours)
        ? 'calendar'
        : 'openingHours',
    openingHours: prefilledOpeningHours,
    hasStartDate: HasDateEnum.NO, //  TODO : retrieve the openingHours startDate when it exists on the model
    hasEndDate: HasDateEnum.NO, //  TODO : retrieve the openingHours endDate when it exists on the model
    startDate: null, //  TODO : retrieve the openingHours startDate when it exists on the model
    endDate: null, //  TODO : retrieve the openingHours endDate when it exists on the model
    quantityPerPriceCategories:
      !areOpeningHoursEmpty(openingHours) && stocks && stocks.length > 0
        ? stocks.map((stock) => ({
            priceCategory: stock.priceCategoryId?.toString() || '',
            quantity: stock.quantity,
          }))
        : [{ priceCategory: offer.priceCategories?.[0]?.id.toString() || '' }],
  } satisfies IndividualOfferTimetableFormValues
}
