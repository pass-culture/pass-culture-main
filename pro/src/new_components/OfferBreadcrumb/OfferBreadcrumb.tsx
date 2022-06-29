import Breadcrumb, {
  BreadcrumbStyle,
} from 'new_components/Breadcrumb/Breadcrumb'
import {
  useOfferEditionURL,
  useOfferStockEditionURL,
} from 'components/hooks/useOfferEditionURL'

import React from 'react'
import type { Step } from 'new_components/Breadcrumb'
import useActiveFeature from 'components/hooks/useActiveFeature'

export enum OfferBreadcrumbStep {
  DETAILS = 'details',
  STOCKS = 'stocks',
  VISIBILITY = 'visibility',
  SUMMARY = 'recapitulatif',
  CONFIRMATION = 'confirmation',
}

interface IOfferBreadcrumb {
  activeStep: OfferBreadcrumbStep
  isCreatingOffer: boolean
  offerId?: string
  isOfferEducational?: boolean
  className?: string
  haveStock?: boolean
  submitStepForm?: (onSuccessRedirectUrl: string) => void
}

const OfferBreadcrumb = ({
  activeStep,
  isCreatingOffer,
  offerId = '',
  isOfferEducational = false,
  className,
  haveStock = false,
  submitStepForm,
}: IOfferBreadcrumb): JSX.Element => {
  const enableEducationalInstitutionAssociation = useActiveFeature(
    'ENABLE_EDUCATIONAL_INSTITUTION_ASSOCIATION'
  )
  const useSummaryPage = useActiveFeature('OFFER_FORM_SUMMARY_PAGE')
  const offerEditionUrl = useOfferEditionURL(isOfferEducational, offerId)
  const stockEditionUrl = useOfferStockEditionURL(isOfferEducational, offerId)

  const isTemplateId = offerId.startsWith('T-')
  let steps: Step[] = []

  if (!isCreatingOffer) {
    steps = [
      {
        id: OfferBreadcrumbStep.DETAILS,
        label: "Détails de l'offre",
        url: offerEditionUrl,
      },
      {
        id: OfferBreadcrumbStep.STOCKS,
        label: isOfferEducational ? 'Date et prix' : 'Stock et prix',
        url: stockEditionUrl,
      },
      ...(isOfferEducational &&
      enableEducationalInstitutionAssociation &&
      !isTemplateId
        ? [
            {
              id: OfferBreadcrumbStep.VISIBILITY,
              label: 'Visibilité',
              url: `/offre/${offerId}/collectif/visibilite/edition`,
            },
          ]
        : []),
      ...(!isOfferEducational && useSummaryPage
        ? [
            {
              id: OfferBreadcrumbStep.SUMMARY,
              label: 'Récapitulatif',
              url: `/offre/${offerId}/individuel/recapitulatif`,
            },
          ]
        : []),
    ]
  } else {
    const stepList: { [key: string]: Step } = {
      [OfferBreadcrumbStep.DETAILS]: {
        id: OfferBreadcrumbStep.DETAILS,
        label: "Détails de l'offre",
      },
      [OfferBreadcrumbStep.STOCKS]: {
        id: OfferBreadcrumbStep.STOCKS,
        label: isOfferEducational ? 'Date et prix' : 'Stock et prix',
      },
      ...(isOfferEducational && enableEducationalInstitutionAssociation
        ? {
            [OfferBreadcrumbStep.VISIBILITY]: {
              id: OfferBreadcrumbStep.VISIBILITY,
              label: 'Visibilité',
            },
          }
        : {}),
      ...(!isOfferEducational && useSummaryPage
        ? {
            [OfferBreadcrumbStep.SUMMARY]: {
              id: OfferBreadcrumbStep.SUMMARY,
              label: 'Récapitulatif',
            },
          }
        : {}),
      [OfferBreadcrumbStep.CONFIRMATION]: {
        id: OfferBreadcrumbStep.CONFIRMATION,
        label: 'Confirmation',
      },
    }

    if (useSummaryPage && offerId) {
      stepList[
        OfferBreadcrumbStep.DETAILS
      ].url = `/offre/${offerId}/individuel/creation`

      stepList[
        OfferBreadcrumbStep.STOCKS
      ].url = `/offre/${offerId}/individuel/creation/stocks`

      if (haveStock) {
        stepList[
          OfferBreadcrumbStep.SUMMARY
        ].url = `/offre/${offerId}/individuel/creation/recapitulatif`
      }

      if (submitStepForm) {
        Object.keys(stepList).forEach((stepId: string) => {
          const step = stepList[stepId]
          if (step.url) {
            stepList[stepId].onClick = (e: React.MouseEvent) => {
              e.preventDefault()
              step.url && submitStepForm(step.url)
            }
          }
        })
      }
    }

    steps = Object.values(stepList)
  }

  return (
    <Breadcrumb
      activeStep={activeStep}
      className={className}
      steps={steps}
      styleType={
        isCreatingOffer ? BreadcrumbStyle.DEFAULT : BreadcrumbStyle.TAB
      }
    />
  )
}

export default OfferBreadcrumb
