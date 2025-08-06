import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient//v1'
import { isCollectiveOfferTemplate } from '@/commons/core/OfferEducational/types'
import { Step, Stepper } from '@/components/Stepper/Stepper'

export enum CollectiveOfferStep {
  DETAILS = 'details',
  STOCKS = 'stocks',
  VISIBILITY = 'visibility',
  SUMMARY = 'recapitulatif',
  PREVIEW = 'preview',
  CONFIRMATION = 'confirmation',
}

export interface CollectiveCreationOfferNavigationProps {
  activeStep: CollectiveOfferStep
  isTemplate: boolean
  offerId?: number
  className?: string
  requestId?: string | null
  offer?:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
}

export const CollectiveCreationOfferNavigation = ({
  activeStep,
  isTemplate = false,
  offerId = 0,
  className,
  requestId = null,
  offer,
}: CollectiveCreationOfferNavigationProps): JSX.Element => {
  const stepList: { [key in CollectiveOfferStep]?: Step } = {}

  const requestIdUrl = requestId ? `?requete=${requestId}` : ''

  const hasOfferPassedDetailsStep = offer && offerId

  const hasOfferPassedStocksStep =
    hasOfferPassedDetailsStep &&
    (isCollectiveOfferTemplate(offer) || offer.collectiveStock)

  const hasOfferPassedVisibilityStep =
    hasOfferPassedStocksStep &&
    (isCollectiveOfferTemplate(offer) || offer.institution)

  //  Creating an offer
  stepList[CollectiveOfferStep.DETAILS] = {
    id: CollectiveOfferStep.DETAILS,
    label: 'Détails de l’offre',
    url: hasOfferPassedDetailsStep
      ? isTemplate
        ? `/offre/collectif/vitrine/${offerId}/creation`
        : `/offre/collectif/${offerId}/creation${requestIdUrl}`
      : '',
  }

  if (!isTemplate) {
    //  These steps only exist for bookable offers
    stepList[CollectiveOfferStep.STOCKS] = {
      id: CollectiveOfferStep.STOCKS,
      label: 'Dates et prix',
      url:
        hasOfferPassedDetailsStep && !isCollectiveOfferTemplate(offer)
          ? `/offre/${offerId}/collectif/stocks`
          : '',
    }

    stepList[CollectiveOfferStep.VISIBILITY] = {
      id: CollectiveOfferStep.VISIBILITY,
      label: 'Établissement et enseignant',
      url: hasOfferPassedStocksStep
        ? `/offre/${offerId}/collectif/visibilite`
        : '',
    }
  }

  stepList[CollectiveOfferStep.SUMMARY] = {
    id: CollectiveOfferStep.SUMMARY,
    label: 'Récapitulatif',
    url: hasOfferPassedVisibilityStep
      ? isTemplate
        ? `/offre/${offerId}/collectif/vitrine/creation/recapitulatif`
        : `/offre/${offerId}/collectif/creation/recapitulatif`
      : '',
  }
  stepList[CollectiveOfferStep.PREVIEW] = {
    id: CollectiveOfferStep.PREVIEW,
    label: 'Aperçu',
    url: hasOfferPassedVisibilityStep
      ? isTemplate
        ? `/offre/${offerId}/collectif/vitrine/creation/apercu`
        : `/offre/${offerId}/collectif/creation/apercu`
      : '',
  }

  const steps = Object.values(stepList)

  return <Stepper activeStep={activeStep} className={className} steps={steps} />
}
