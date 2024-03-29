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
  offer: CollectiveOfferTemplateResponseModel
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
    'Tout au long de l’année scolaire (l’offre est permanente)'
  )
}

export function getFormattedDatesForBookableOffer(
  offer: CollectiveOfferResponseModel
) {
  return offer.stock.beginningDatetime
    ? `Le ${getDateTimeToFrenchText(
        getLocalDepartementDateTimeFromUtc(
          offer.stock.beginningDatetime,
          offer.venue.departmentCode
        ),
        { dateStyle: 'long', timeStyle: 'short' }
      )}`
    : null
}
