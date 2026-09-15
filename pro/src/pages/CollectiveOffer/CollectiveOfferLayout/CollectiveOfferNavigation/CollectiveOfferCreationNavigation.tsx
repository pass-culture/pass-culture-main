import type { GetCollectiveOfferResponseModel } from '@/apiClient/v1'
import { isCollectiveOfferTemplate } from '@/commons/core/OfferEducational/types'
import { type StepItem, Stepper } from '@/design-system/Stepper/Stepper'

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

  const hasPassedDetailsStep = offer
  const hasPassedStocksStep = hasPassedDetailsStep && offer.collectiveStock
  const hasPassedInstitutionStep = hasPassedStocksStep && offer.institution
  const hasPassedInformationsSteps =
    hasPassedStocksStep &&
    (!!offer.additionalDetails || !!hasPassedInstitutionStep)

  const steps: StepItem[] = [
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

  return (
    <div className={styles['eac-stepper-wrapper']}>
      <Stepper activeStep={activeStep} steps={steps} />
    </div>
  )
}
