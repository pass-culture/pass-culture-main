import type { GetCollectiveOfferResponseModel } from '@/apiClient/v1/new'
import { isCollectiveOfferTemplate } from '@/commons/core/OfferEducational/types'
import { type Step, Stepper } from '@/components/Stepper/Stepper'

import styles from './CollectiveOfferNavigation.module.scss'

export enum CollectiveOfferStep {
  DETAILS = 'details',
  STOCKS = 'stocks',
  INSTITUTION = 'institution',
  SUMMARY = 'recapitulatif',
  PREVIEW = 'preview',
  CONFIRMATION = 'confirmation',
}

export interface CollectiveOfferCreationNavigationProps {
  activeStep: CollectiveOfferStep
  offerId?: number
  requestId?: string | null
  offer?: GetCollectiveOfferResponseModel
}

export const CollectiveOfferCreationNavigation = ({
  activeStep,
  offerId = 0,
  requestId = null,
  offer,
}: CollectiveOfferCreationNavigationProps): JSX.Element => {
  const requestIdUrl = requestId ? `?requete=${requestId}` : ''

  const hasPassedDetailsStep = offer && offerId
  const hasPassedStocksStep = hasPassedDetailsStep && offer.collectiveStock
  const hasPassedVisibilityStep = hasPassedStocksStep && offer.institution

  const stepList: { [key in CollectiveOfferStep]?: Step } = {}
  stepList[CollectiveOfferStep.DETAILS] = {
    id: CollectiveOfferStep.DETAILS,
    label: "Détails de l'offre",
    url: hasPassedDetailsStep
      ? `/offre/collectif/${offerId}/creation${requestIdUrl}`
      : '',
  }
  stepList[CollectiveOfferStep.STOCKS] = {
    id: CollectiveOfferStep.STOCKS,
    label: 'Dates et prix',
    url:
      hasPassedDetailsStep && !isCollectiveOfferTemplate(offer)
        ? `/offre/${offerId}/collectif/stocks`
        : '',
  }

  stepList[CollectiveOfferStep.INSTITUTION] = {
    id: CollectiveOfferStep.INSTITUTION,
    label: 'Établissement et enseignant',
    url: hasPassedStocksStep ? `/offre/${offerId}/collectif/etablissement` : '',
  }

  stepList[CollectiveOfferStep.SUMMARY] = {
    id: CollectiveOfferStep.SUMMARY,
    label: 'Récapitulatif',
    url: hasPassedVisibilityStep
      ? `/offre/${offerId}/collectif/creation/recapitulatif`
      : '',
  }
  stepList[CollectiveOfferStep.PREVIEW] = {
    id: CollectiveOfferStep.PREVIEW,
    label: 'Aperçu',
    url: hasPassedVisibilityStep
      ? `/offre/${offerId}/collectif/creation/apercu`
      : '',
  }

  const steps = Object.values(stepList)

  return (
    <Stepper
      activeStep={activeStep}
      className={styles['eac-stepper']}
      steps={steps}
    />
  )
}
