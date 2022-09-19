export const extractOfferIdFromObjectId = (offerId: string): number => {
  const splitResult = offerId.split('T-')

  if (splitResult.length === 2) {
    return Number(splitResult[1])
  }

  return Number(offerId)
}
