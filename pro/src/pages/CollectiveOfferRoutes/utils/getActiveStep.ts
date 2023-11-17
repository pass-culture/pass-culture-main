import { CollectiveOfferNavigationStep } from 'components/CollectiveOfferNavigation'

export const getActiveStep = (
  locationPathname: string
): CollectiveOfferNavigationStep => {
  if (locationPathname.includes('stocks')) {
    return CollectiveOfferNavigationStep.STOCKS
  }

  if (locationPathname.includes('visibilite')) {
    return CollectiveOfferNavigationStep.VISIBILITY
  }

  if (locationPathname.includes('recapitulatif')) {
    return CollectiveOfferNavigationStep.SUMMARY
  }

  return CollectiveOfferNavigationStep.DETAILS
}
