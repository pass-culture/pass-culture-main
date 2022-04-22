export const extractOfferIdAndOfferTypeFromRouteParams = (
  offerIdFromParams: string
): { offerId: string; isShowcase: boolean } => {
  const splitResult = offerIdFromParams.split('T-')

  if (splitResult.length === 2) {
    return { offerId: splitResult[1], isShowcase: true }
  }

  return { offerId: offerIdFromParams, isShowcase: false }
}
