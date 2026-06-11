import type { GetCollectiveOfferResponseModel } from '@/apiClient/v1/new'
import { isCollectiveOfferTemplate } from '@/commons/core/OfferEducational/types'
import { type Step, Stepper } from '@/components/Stepper/Stepper'

import styles from './CollectiveOfferNavigation.module.scss'
import { CollectiveOfferStep } from './constants'

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
  const hasPassedInstitutionStep = hasPassedStocksStep && offer.institution

  const steps: Step[] = [
    {
      id: CollectiveOfferStep.DETAILS,
      label: "Détails de l'offre",
      url: hasPassedDetailsStep
        ? `/offre/collectif/${offerId}/creation${requestIdUrl}`
        : '',
    },
    {
      id: CollectiveOfferStep.STOCKS,
      label: 'Dates et prix',
      url:
        hasPassedDetailsStep && !isCollectiveOfferTemplate(offer)
          ? `/offre/${offerId}/collectif/stocks`
          : '',
    },

    {
      id: CollectiveOfferStep.INSTITUTION,
      label: 'Établissement et enseignant',
      url: hasPassedStocksStep
        ? `/offre/${offerId}/collectif/etablissement`
        : '',
    },

    {
      id: CollectiveOfferStep.SUMMARY,
      label: 'Récapitulatif',
      url: hasPassedInstitutionStep
        ? `/offre/${offerId}/collectif/creation/recapitulatif`
        : '',
    },
    {
      id: CollectiveOfferStep.PREVIEW,
      label: 'Aperçu',
      url: hasPassedInstitutionStep
        ? `/offre/${offerId}/collectif/creation/apercu`
        : '',
    },
  ]

  return (
    <Stepper
      activeStep={activeStep}
      className={styles['eac-stepper']}
      steps={steps}
    />
  )
}
