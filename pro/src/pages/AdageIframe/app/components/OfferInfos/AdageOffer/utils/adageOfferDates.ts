import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'
import { getDateTimeToFrenchText, getRangeToFrenchText } from 'utils/date'
import { getLocalDepartementDateTimeFromUtc } from 'utils/timezone'

export function getFormattedDatesForTemplateOffer(
  offer: CollectiveOfferTemplateResponseModel
) {
  return (
    (offer.dates?.start &&
      offer.dates?.end &&
      getRangeToFrenchText(
        getLocalDepartementDateTimeFromUtc(
          offer.dates.start,
          offer.venue.departmentCode
        ),
        getLocalDepartementDateTimeFromUtc(
          offer.dates.end,
          offer.venue.departmentCode
        )
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
