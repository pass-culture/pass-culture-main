import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'
import {
  getDateTimeToFrenchText,
  getRangeToFrenchText,
  toDateStrippedOfTimezone,
} from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

export function getFormattedDatesForTemplateOffer(
  offer: CollectiveOfferTemplateResponseModel,
  noDatesWording: string = 'Tout au long de l’année scolaire (l’offre est permanente)'
) {
  // Template offer start & end dates timezone is to be ignored. A date entered in pro UI as "2024-01-25" at "15:15"
  //  is saved as "2024-01-25T15:15:00Z" and thus should be displayed as "Le 25 janvier 2024 à 15h15"
  return (
    (offer.dates?.start &&
      offer.dates.end &&
      getRangeToFrenchText(
        toDateStrippedOfTimezone(offer.dates.start),
        toDateStrippedOfTimezone(offer.dates.end)
      )) ||
    noDatesWording
  )
}

export function getFormattedDatesForBookableOffer(
  offer: CollectiveOfferResponseModel
) {
  return offer.stock.startDatetime
    ? `Le ${getDateTimeToFrenchText(
        getLocalDepartementDateTimeFromUtc(
          offer.stock.startDatetime,
          offer.venue.departmentCode
        ),
        { dateStyle: 'long', timeStyle: 'short' }
      )}`
    : null
}
