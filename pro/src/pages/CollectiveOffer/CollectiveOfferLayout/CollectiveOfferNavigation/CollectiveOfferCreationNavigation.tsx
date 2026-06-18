import type { GetCollectiveOfferResponseModel } from '@/apiClient/v1/new'
import { isCollectiveOfferTemplate } from '@/commons/core/OfferEducational/types'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { type Step, Stepper } from '@/components/Stepper/Stepper'

import styles from './CollectiveOfferNavigation.module.scss'
import { CollectiveOfferStep } from './constants'

export interface CollectiveOfferCreationNavigationProps {
  activeStep: CollectiveOfferStep
  requestId?: string | null
  offer?: GetCollectiveOfferResponseModel
}

export const CollectiveOfferCreationNavigation = ({
  activeStep,
  requestId = null,
  offer,
}: CollectiveOfferCreationNavigationProps): JSX.Element => {
  const requestIdUrl = requestId ? `?requete=${requestId}` : ''

  const isNewCollectivePriceEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS'
  )

  const hasPassedDetailsStep = offer
  const hasPassedStocksStep = hasPassedDetailsStep && offer.collectiveStock
  const hasPassedInformationsSteps =
    hasPassedStocksStep &&
    (!isNewCollectivePriceEnabled || !!offer.additionalDetails)
  const hasPassedInstitutionStep = hasPassedStocksStep && offer.institution

  let steps: Step[] = [
    {
      id: CollectiveOfferStep.DETAILS,
      label: "Détails de l'offre",
      url: hasPassedDetailsStep
        ? `/offre/collectif/${offer.id}/creation${requestIdUrl}`
        : '',
    },
    {
      id: CollectiveOfferStep.STOCKS,
      label: 'Dates et prix',
      url:
        hasPassedDetailsStep && !isCollectiveOfferTemplate(offer)
          ? `/offre/${offer.id}/collectif/stocks`
          : '',
    },
    {
      id: CollectiveOfferStep.INFORMATION,
      label: 'Informations pratiques',
      url: hasPassedStocksStep
        ? `/offre/${offer.id}/collectif/informations-pratiques`
        : '',
    },
    {
      id: CollectiveOfferStep.INSTITUTION,
      label: 'Établissement et enseignant',
      url: hasPassedInformationsSteps
        ? `/offre/${offer.id}/collectif/etablissement`
        : '',
    },
    {
      id: CollectiveOfferStep.SUMMARY,
      label: 'Récapitulatif',
      url: hasPassedInstitutionStep
        ? `/offre/${offer.id}/collectif/creation/recapitulatif`
        : '',
    },
    {
      id: CollectiveOfferStep.PREVIEW,
      label: 'Aperçu',
      url: hasPassedInstitutionStep
        ? `/offre/${offer.id}/collectif/creation/apercu`
        : '',
    },
  ]

  if (!isNewCollectivePriceEnabled) {
    steps = steps.filter((s) => s.id !== CollectiveOfferStep.INFORMATION)
  }

  return (
    <Stepper
      activeStep={activeStep}
      className={styles['eac-stepper']}
      steps={steps}
    />
  )
}
