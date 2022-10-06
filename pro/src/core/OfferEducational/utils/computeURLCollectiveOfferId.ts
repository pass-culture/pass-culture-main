export const computeURLCollectiveOfferId = (
  offerId: string,
  isTemplate: boolean
): string => `${isTemplate ? 'T-' : ''}${offerId}`
