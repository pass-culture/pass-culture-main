import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import { isCollectiveOfferTemplate } from 'commons/core/OfferEducational/types'
import { Step, Stepper } from 'components/Stepper/Stepper'

export enum CollectiveOfferStep {
  DETAILS = 'details',
  STOCKS = 'stocks',
  VISIBILITY = 'visibility',
  SUMMARY = 'recapitulatif',
  CONFIRMATION = 'confirmation',
  PREVIEW = 'preview',
}

export interface CollectiveOfferNavigationProps {
  activeStep: CollectiveOfferStep
  isTemplate: boolean
  offerId?: number
  className?: string
  requestId?: string | null
  offer?:
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
}

export const CollectiveOfferNavigation = ({
  activeStep,
  isTemplate = false,
  offerId = 0,
  className,
  requestId = null,
  offer,
}: CollectiveOfferNavigationProps): JSX.Element => {
  const stepList: { [key in CollectiveOfferStep]?: Step } = {}

  const requestIdUrl = requestId ? `?requete=${requestId}` : ''

  //  Creating an offer
  stepList[CollectiveOfferStep.DETAILS] = {
    id: CollectiveOfferStep.DETAILS,
    label: 'Détails de l’offre',
  }
  if (!isTemplate) {
    //  These steps only exist for bookable offers
    stepList[CollectiveOfferStep.STOCKS] = {
      id: CollectiveOfferStep.STOCKS,
      label: 'Dates et prix',
    }

    stepList[CollectiveOfferStep.VISIBILITY] = {
      id: CollectiveOfferStep.VISIBILITY,
      label: 'Établissement et enseignant',
    }
  }
  stepList[CollectiveOfferStep.SUMMARY] = {
    id: CollectiveOfferStep.SUMMARY,
    label: 'Récapitulatif',
  }
  stepList[CollectiveOfferStep.PREVIEW] = {
    id: CollectiveOfferStep.PREVIEW,
    label: 'Aperçu',
  }
  stepList[CollectiveOfferStep.CONFIRMATION] = {
    id: CollectiveOfferStep.CONFIRMATION,
    label: 'Confirmation',
  }

  const hasOfferPassedDetailsStep = offer && offerId
  const hasOfferPassedStocksStep =
    hasOfferPassedDetailsStep &&
    (isCollectiveOfferTemplate(offer) || offer.collectiveStock)
  const hasOfferPassedVisibilityStep =
    hasOfferPassedStocksStep &&
    (isCollectiveOfferTemplate(offer) || offer.institution)

  if (hasOfferPassedDetailsStep) {
    //  The user can go back to the details page after it has been filled the first time
    stepList[CollectiveOfferStep.DETAILS].url = isTemplate
      ? `/offre/collectif/vitrine/${offerId}/creation`
      : `/offre/collectif/${offerId}/creation${requestIdUrl}`

    if (
      !isCollectiveOfferTemplate(offer) &&
      stepList[CollectiveOfferStep.STOCKS]
    ) {
      //  The stocks step is accessible when the details form has been filled and the offer is bookable
      stepList[CollectiveOfferStep.STOCKS].url =
        `/offre/${offerId}/collectif/stocks`
    }
  }

  if (hasOfferPassedStocksStep && stepList[CollectiveOfferStep.VISIBILITY]) {
    //  The visibility tab is only accessible when the stocks form has been filled
    stepList[CollectiveOfferStep.VISIBILITY].url =
      `/offre/${offerId}/collectif/visibilite`
  }

  if (hasOfferPassedVisibilityStep) {
    //  The summary tab is only accessible when the visibility form has been filled (or the offer is a template)
    stepList[CollectiveOfferStep.SUMMARY].url = isTemplate
      ? `/offre/${offerId}/collectif/vitrine/creation/recapitulatif`
      : `/offre/${offerId}/collectif/creation/recapitulatif`

    stepList[CollectiveOfferStep.PREVIEW].url = isTemplate
      ? `/offre/${offerId}/collectif/vitrine/creation/apercu`
      : `/offre/${offerId}/collectif/creation/apercu`
  }
  // }

  const steps = Object.values(stepList)

  return <Stepper activeStep={activeStep} className={className} steps={steps} />
}
