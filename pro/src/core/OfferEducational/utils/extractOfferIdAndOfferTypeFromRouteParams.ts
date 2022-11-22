export const extractOfferIdAndOfferTypeFromRouteParams = (
  offerIdFromParams: string
): { offerId: string; isTemplate: boolean } => {
  const splitResult = offerIdFromParams.split('T-')

  if (splitResult.length === 2) {
    return { offerId: splitResult[1], isTemplate: true }
  }

  return { offerId: offerIdFromParams, isTemplate: false }
}
