import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from '@/apiClient/adage'
import {
  getDateTimeToFrenchText,
  getRangeToFrenchText,
  toDateStrippedOfTimezone,
} from '@/commons/utils/date'
import { getLocalDepartementDateTimeFromUtc } from '@/commons/utils/timezone'

export function getFormattedDatesForTemplateOffer(
  offer: CollectiveOfferTemplateResponseModel,
  noDatesWording: string = 'Tout au long de l’année scolaire (l’offre est permanente)'
) {
  // Template offer start & end dates timezone is to be ignored. A date entered in pro UI as "2024-01-25" at "15:15"
  //  is saved as "2024-01-25T15:15:00Z" and thus should be displayed as "Le 25 janvier 2024 à 15h15"

  if (!offer.dates?.start || !offer.dates.end) {
    return noDatesWording
  }
  const start = toDateStrippedOfTimezone(offer.dates.start)
  const end = toDateStrippedOfTimezone(offer.dates.end)
  return getRangeToFrenchText(
    start,
    end,
    start.getHours() !== 0 || start.getMinutes() !== 0
  )
}

export function getFormattedDatesForBookableOffer(
  offer: CollectiveOfferResponseModel
) {
  if (!offer.stock.startDatetime || !offer.stock.endDatetime) {
    return null
  }
  if (offer.stock.startDatetime === offer.stock.endDatetime) {
    return `Le ${getDateTimeToFrenchText(
      getLocalDepartementDateTimeFromUtc(
        offer.stock.startDatetime,
        offer.venue.departmentCode
      ),
      { dateStyle: 'long', timeStyle: 'short' }
    )}`
  }

  return getRangeToFrenchText(
    getLocalDepartementDateTimeFromUtc(
      offer.stock.startDatetime,
      offer.venue.departmentCode
    ),
    getLocalDepartementDateTimeFromUtc(
      offer.stock.endDatetime,
      offer.venue.departmentCode
    ),
    true
  )
}
