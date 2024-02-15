import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'
import {
  getDateTimeToFrenchText,
  getRangeToFrenchText,
  toDateStrippedOfTimezone,
} from 'utils/date'

export function getFormattedDatesForTemplateOffer(
  offer: CollectiveOfferTemplateResponseModel
) {
  return (
    (offer.dates?.start &&
      offer.dates?.end &&
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
        toDateStrippedOfTimezone(offer.stock.beginningDatetime),
        { dateStyle: 'long', timeStyle: 'short' }
      )}`
    : null
}
