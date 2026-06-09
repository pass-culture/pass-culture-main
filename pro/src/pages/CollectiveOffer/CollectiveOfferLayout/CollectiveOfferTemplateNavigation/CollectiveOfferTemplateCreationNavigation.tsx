import type { GetCollectiveOfferTemplateResponseModel } from '@/apiClient/v1/new'
import { type Step, Stepper } from '@/components/Stepper/Stepper'

import styles from './CollectiveOfferTemplateNavigation.module.scss'
import { CollectiveOfferTemplateStep } from './constants'

export type CollectiveOfferTemplateCreationNavigationProps = {
  activeStep: CollectiveOfferTemplateStep
  offerId?: number
  offer?: GetCollectiveOfferTemplateResponseModel
}

export const CollectiveOfferTemplateCreationNavigation = ({
  activeStep,
  offerId = 0,
  offer,
}: CollectiveOfferTemplateCreationNavigationProps): JSX.Element => {
  const isOfferTemplateCreated = offer && offerId

  const stepList: Step[] = [
    {
      id: CollectiveOfferTemplateStep.DETAILS,
      label: 'Détails de l’offre',
      url: isOfferTemplateCreated
        ? `/offre/collectif/vitrine/${offerId}/creation`
        : '',
    },
    {
      id: CollectiveOfferTemplateStep.SUMMARY,
      label: 'Récapitulatif',
      url: isOfferTemplateCreated
        ? `/offre/${offer.id}/collectif/vitrine/creation/recapitulatif`
        : '',
    },
    {
      id: CollectiveOfferTemplateStep.PREVIEW,
      label: 'Aperçu',
      url: isOfferTemplateCreated
        ? `/offre/${offer.id}/collectif/vitrine/creation/apercu`
        : '',
    },
  ]

  const steps = Object.values(stepList)

  return (
    <Stepper
      activeStep={activeStep}
      className={styles['eac-stepper']}
      steps={steps}
    />
  )
}
