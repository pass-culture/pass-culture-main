import { OfferStatus } from 'apiClient/v1'
import { Offer } from 'core/Offers/types'

export function canDeleteOffers(
  offers: Offer[],
  tmpSelectedOfferIds: string[]
): boolean {
  const selectedOffers = offers.filter((offer) =>
    tmpSelectedOfferIds.includes(offer.id.toString())
  )
  return selectedOffers.every((offer) => offer.status === OfferStatus.DRAFT)
}
