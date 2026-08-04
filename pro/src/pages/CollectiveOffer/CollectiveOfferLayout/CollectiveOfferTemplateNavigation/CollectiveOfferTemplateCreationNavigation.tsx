import type { GetCollectiveOfferTemplateResponseModel } from '@/apiClient/v1'
import { type StepItem, Stepper } from '@/design-system/Stepper/Stepper'

import styles from './CollectiveOfferTemplateNavigation.module.scss'
import { CollectiveOfferTemplateStep } from './constants'

export type CollectiveOfferTemplateCreationNavigationProps = {
  activeStep: CollectiveOfferTemplateStep
  offer?: GetCollectiveOfferTemplateResponseModel
}

export const CollectiveOfferTemplateCreationNavigation = ({
  activeStep,
  offer,
}: CollectiveOfferTemplateCreationNavigationProps): JSX.Element => {
  const isOfferTemplateCreated = !!offer

  const stepList: StepItem[] = [
    {
      id: CollectiveOfferTemplateStep.DETAILS,
      label: 'Détails de l’offre',
      url: isOfferTemplateCreated
        ? `/offre/collectif/vitrine/${offer.id}/creation`
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
    <div className={styles['eac-stepper-wrapper']}>
      <Stepper activeStep={activeStep} steps={steps} />
    </div>
  )
}
