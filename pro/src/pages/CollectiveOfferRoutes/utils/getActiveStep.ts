import { CollectiveOfferBreadcrumbStep } from 'components/CollectiveOfferBreadcrumb'

export const getActiveStep = (
  locationPathname: string
): CollectiveOfferBreadcrumbStep => {
  if (locationPathname.includes('stocks')) {
    return CollectiveOfferBreadcrumbStep.STOCKS
  }

  if (locationPathname.includes('visibilite')) {
    return CollectiveOfferBreadcrumbStep.VISIBILITY
  }

  if (locationPathname.includes('recapitulatif')) {
    return CollectiveOfferBreadcrumbStep.SUMMARY
  }

  return CollectiveOfferBreadcrumbStep.DETAILS
}
