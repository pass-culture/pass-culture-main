import { CollectiveOfferStep } from '@/pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferNavigation/CollectiveCreationOfferNavigation'

export const getActiveStep = (
  locationPathname: string
): CollectiveOfferStep => {
  if (locationPathname.includes('stocks')) {
    return CollectiveOfferStep.STOCKS
  }

  if (locationPathname.includes('etablissement')) {
    return CollectiveOfferStep.INSTITUTION
  }

  if (locationPathname.includes('recapitulatif')) {
    return CollectiveOfferStep.SUMMARY
  }

  if (locationPathname.includes('apercu')) {
    return CollectiveOfferStep.PREVIEW
  }

  return CollectiveOfferStep.DETAILS
}
