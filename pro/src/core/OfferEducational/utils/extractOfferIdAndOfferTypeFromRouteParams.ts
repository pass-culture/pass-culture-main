export const extractOfferIdAndOfferTypeFromRouteParams = (
  offerIdFromParams: string
): { offerId: number; isTemplateId: boolean } => {
  const splitResult = offerIdFromParams.split('T-')
  if (splitResult.length === 2) {
    return { offerId: Number(splitResult[1]), isTemplateId: true }
  }
  return {
    offerId: Number(offerIdFromParams),
    isTemplateId: false,
  }
}
