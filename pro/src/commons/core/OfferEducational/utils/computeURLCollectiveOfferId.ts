export const computeURLCollectiveOfferId = (
  offerId: number,
  isTemplate?: boolean
): string => `${isTemplate ? 'T-' : ''}${offerId}`
