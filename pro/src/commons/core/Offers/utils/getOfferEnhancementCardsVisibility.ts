import {
  type GetIndividualOfferResponseModel,
  OfferStatus,
} from '@/apiClient/v1'

type OfferEnhancementCardsVisibility = {
  shouldDisplayRecommendationCard: boolean
  shouldDisplayHighlightCard: boolean
  shouldDisplayHeadlineCard: boolean
}

export const getOfferEnhancementCardsVisibility = (
  offer: GetIndividualOfferResponseModel | null
): OfferEnhancementCardsVisibility => {
  if (!offer) {
    return {
      shouldDisplayRecommendationCard: false,
      shouldDisplayHighlightCard: false,
      shouldDisplayHeadlineCard: false,
    }
  }

  const isProduct = !!offer.productId
  const hasImage = !!offer.thumbUrl

  // Headline offers without an image are forbidden, and product-based offers
  // cannot have their image edited, so an imageless product-based offer can
  // never become a headline.
  const isNotAProductWithoutImage = !isProduct || hasImage

  return {
    shouldDisplayRecommendationCard: ![
      OfferStatus.PENDING,
      OfferStatus.REJECTED,
      OfferStatus.DRAFT,
    ].includes(offer.status),
    shouldDisplayHighlightCard:
      ![OfferStatus.PENDING, OfferStatus.REJECTED, OfferStatus.DRAFT].includes(
        offer.status
      ) && offer.isEvent,
    shouldDisplayHeadlineCard:
      offer.status === OfferStatus.ACTIVE && isNotAProductWithoutImage,
  }
}
