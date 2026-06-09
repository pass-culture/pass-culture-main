import { CollectiveOfferStep } from '../CollectiveOfferNavigation/constants'
import { CollectiveOfferTemplateStep } from '../CollectiveOfferTemplateNavigation/constants'

export const getCollectiveOfferActiveStep = (
  locationPathname: string
): CollectiveOfferStep => {
  if (locationPathname.includes('stocks')) {
    return CollectiveOfferStep.STOCKS
  }

  if (locationPathname.includes('informations-pratiques')) {
    return CollectiveOfferStep.INFORMATIONS
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

export const getCollectiveOfferTemplateActiveStep = (
  locationPathname: string
): CollectiveOfferTemplateStep => {
  if (locationPathname.includes('recapitulatif')) {
    return CollectiveOfferTemplateStep.SUMMARY
  }

  if (locationPathname.includes('apercu')) {
    return CollectiveOfferTemplateStep.PREVIEW
  }

  return CollectiveOfferTemplateStep.DETAILS
}
