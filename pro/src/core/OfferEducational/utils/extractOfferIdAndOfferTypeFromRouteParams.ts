export const extractOfferIdAndOfferTypeFromRouteParams = (
  offerIdFromParams: string
): { offerId: string; isTemplateId: boolean } => {
  const splitResult = offerIdFromParams.split('T-')
  if (splitResult.length === 2) {
    return { offerId: splitResult[1], isTemplateId: true }
  }
  return {
    offerId: offerIdFromParams,
    isTemplateId: false,
  }
}
