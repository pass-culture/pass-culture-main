import { CollectiveOfferStep } from 'components/CollectiveOfferNavigation'

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

  return CollectiveOfferStep.DETAILS
}
