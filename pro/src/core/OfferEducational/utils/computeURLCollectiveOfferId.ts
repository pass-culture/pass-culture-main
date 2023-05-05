export const computeURLCollectiveOfferId = (
  offerId: number,
  isTemplate: boolean
): string => `${isTemplate ? 'T-' : ''}${offerId}`

// Can be deleted once the offer list has been dehumanized
export const legacyComputeURLCollectiveOfferId = (
  offerId: string,
  isTemplate: boolean
): string => `${isTemplate ? 'T-' : ''}${offerId}`
