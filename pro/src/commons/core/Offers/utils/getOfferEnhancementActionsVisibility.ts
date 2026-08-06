import {
  type GetIndividualOfferResponseModel,
  type ListOffersOfferResponseModel,
  OfferStatus,
} from '@/apiClient/v1'

type OfferEnhancementCardsVisibility = {
  shouldDisplayRecommendationAction: boolean
  shouldDisplayHighlightAction: boolean
  shouldDisplayHeadlineAction: boolean
}

export const getOfferEnhancementActionsVisibility = (
  offer: GetIndividualOfferResponseModel | ListOffersOfferResponseModel | null
): OfferEnhancementCardsVisibility => {
  if (!offer) {
    return {
      shouldDisplayRecommendationAction: false,
      shouldDisplayHighlightAction: false,
      shouldDisplayHeadlineAction: false,
    }
  }

  const isProduct = !!offer.productId
  const hasImage = !!offer.thumbUrl

  // Headline offers without an image are forbidden, and product-based offers
  // cannot have their image edited, so an imageless product-based offer can
  // never become a headline.
  const isNotAProductWithoutImage = !isProduct || hasImage

  return {
    shouldDisplayRecommendationAction: ![
      OfferStatus.PENDING,
      OfferStatus.REJECTED,
      OfferStatus.DRAFT,
    ].includes(offer.status),
    shouldDisplayHighlightAction:
      ![OfferStatus.PENDING, OfferStatus.REJECTED, OfferStatus.DRAFT].includes(
        offer.status
      ) && offer.isEvent,
    shouldDisplayHeadlineAction:
      offer.status === OfferStatus.ACTIVE && isNotAProductWithoutImage,
  }
}
