import { addDays, isAfter } from 'date-fns'

import {
  CollectiveBookingStatus,
  CollectiveOfferResponseModel,
  CollectiveOfferStatus,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import { isCollectiveOfferTemplate } from 'commons/core/OfferEducational/types'

// TODO: delete the functions in this file when the ticket front is finished : https://passculture.atlassian.net/browse/PC-30662
export function canArchiveCollectiveOffer(offer: CollectiveOfferResponseModel) {
  if (offer.status === CollectiveOfferStatus.ARCHIVED) {
    return false
  }

  const startDatetime = offer.stocks[0].startDatetime

  const canArchiveThisOffer =
    offer.status === CollectiveOfferStatus.ACTIVE ||
    offer.status === CollectiveOfferStatus.REJECTED ||
    offer.status === CollectiveOfferStatus.INACTIVE ||
    offer.status === CollectiveOfferStatus.DRAFT ||
    (offer.status === CollectiveOfferStatus.EXPIRED &&
      (!offer.booking?.booking_status ||
        offer.booking.booking_status === CollectiveBookingStatus.CANCELLED)) ||
    Boolean(
      offer.booking?.booking_status === CollectiveBookingStatus.REIMBURSED ||
        (offer.booking?.booking_status === CollectiveBookingStatus.USED &&
          startDatetime &&
          isAfter(new Date(), addDays(new Date(startDatetime), 2)))
    )

  return canArchiveThisOffer
}

export function canArchiveCollectiveOfferFromSummary(
  offer:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
) {
  if (offer.status === CollectiveOfferStatus.ARCHIVED) {
    return false
  }
  if (isCollectiveOfferTemplate(offer)) {
    const canArchiveThisOffer =
      offer.status === CollectiveOfferStatus.ACTIVE ||
      offer.status === CollectiveOfferStatus.REJECTED ||
      offer.status === CollectiveOfferStatus.INACTIVE ||
      offer.status === CollectiveOfferStatus.DRAFT

    return canArchiveThisOffer
  } else {
    const startDatetime = offer.collectiveStock?.startDatetime

    const canArchiveThisOffer =
      offer.status === CollectiveOfferStatus.ACTIVE ||
      offer.status === CollectiveOfferStatus.REJECTED ||
      offer.status === CollectiveOfferStatus.INACTIVE ||
      offer.status === CollectiveOfferStatus.DRAFT ||
      (offer.status === CollectiveOfferStatus.EXPIRED &&
        (!offer.lastBookingStatus ||
          offer.lastBookingStatus === CollectiveBookingStatus.CANCELLED)) ||
      Boolean(
        offer.lastBookingStatus === CollectiveBookingStatus.REIMBURSED ||
          (offer.lastBookingStatus === CollectiveBookingStatus.USED &&
            startDatetime &&
            isAfter(new Date(), addDays(new Date(startDatetime), 2)))
      )

    return canArchiveThisOffer
  }
}
