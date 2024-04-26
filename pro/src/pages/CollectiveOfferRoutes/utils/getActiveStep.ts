import { CollectiveOfferStep } from 'components/CollectiveOfferNavigation/CollectiveOfferNavigation'

export const getActiveStep = (
  locationPathname: string
): CollectiveOfferStep => {
  if (locationPathname.includes('stocks')) {
    return CollectiveOfferStep.STOCKS
  }

  if (locationPathname.includes('visibilite')) {
    return CollectiveOfferStep.VISIBILITY
  }

  if (locationPathname.includes('recapitulatif')) {
    return CollectiveOfferStep.SUMMARY
  }

  if (locationPathname.includes('apercu')) {
    return CollectiveOfferStep.PREVIEW
  }

  return CollectiveOfferStep.DETAILS
}
