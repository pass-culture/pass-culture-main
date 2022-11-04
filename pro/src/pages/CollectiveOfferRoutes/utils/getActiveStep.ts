import { OfferBreadcrumbStep } from 'components/OfferBreadcrumb'

export const getActiveStep = (
  locationPathname: string
): OfferBreadcrumbStep => {
  if (locationPathname.includes('stocks')) {
    return OfferBreadcrumbStep.STOCKS
  }

  if (locationPathname.includes('visibilite')) {
    return OfferBreadcrumbStep.VISIBILITY
  }

  if (locationPathname.includes('recapitulatif')) {
    return OfferBreadcrumbStep.SUMMARY
  }

  return OfferBreadcrumbStep.DETAILS
}
