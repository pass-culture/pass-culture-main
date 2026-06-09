import type { GetCollectiveOfferTemplateResponseModel } from '@/apiClient/v1'
import { type Step, Stepper } from '@/components/Stepper/Stepper'

import { CollectiveOfferStep } from '../CollectiveOfferNavigation/CollectiveOfferCreationNavigation'
import styles from './CollectiveOfferTemplateNavigation.module.scss'

export type CollectiveOfferTemplateCreationNavigationProps = {
  activeStep: CollectiveOfferStep
  offerId?: number
  offer?: GetCollectiveOfferTemplateResponseModel
}

export const CollectiveOfferTemplateCreationNavigation = ({
  activeStep,
  offerId = 0,
  offer,
}: CollectiveOfferTemplateCreationNavigationProps): JSX.Element => {
  const isOfferTemplateCreated = offer && offerId

  const stepList: { [key in CollectiveOfferStep]?: Step } = {}

  stepList[CollectiveOfferStep.DETAILS] = {
    id: CollectiveOfferStep.DETAILS,
    label: 'Détails de l’offre',
    url: isOfferTemplateCreated
      ? `/offre/collectif/vitrine/${offerId}/creation`
      : '',
  }

  stepList[CollectiveOfferStep.SUMMARY] = {
    id: CollectiveOfferStep.SUMMARY,
    label: 'Récapitulatif',
    url: isOfferTemplateCreated
      ? `/offre/${offerId}/collectif/vitrine/creation/recapitulatif`
      : '',
  }
  stepList[CollectiveOfferStep.PREVIEW] = {
    id: CollectiveOfferStep.PREVIEW,
    label: 'Aperçu',
    url: isOfferTemplateCreated
      ? `/offre/${offerId}/collectif/vitrine/creation/apercu`
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
