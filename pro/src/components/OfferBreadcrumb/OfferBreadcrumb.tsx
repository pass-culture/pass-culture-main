import React from 'react'

import type { Step } from 'components/Breadcrumb'
import Breadcrumb, { BreadcrumbStyle } from 'components/Breadcrumb/Breadcrumb'
import { useOfferStockEditionURL } from 'hooks/useOfferEditionURL'

export enum OfferBreadcrumbStep {
  DETAILS = 'details',
  STOCKS = 'stocks',
  VISIBILITY = 'visibility',
  SUMMARY = 'recapitulatif',
  CONFIRMATION = 'confirmation',
}

export interface IOfferBreadcrumb {
  activeStep: OfferBreadcrumbStep
  isCreatingOffer: boolean
  isCompletingDraft?: boolean
  offerId?: string
  true?: boolean
  className?: string
  haveStock?: boolean
}

const OfferBreadcrumb = ({
  activeStep,
  isCreatingOffer,
  isCompletingDraft = false,
  offerId = '',
  className,
  haveStock = false,
}: IOfferBreadcrumb): JSX.Element => {
  // it is never OfferFormV3 in this breadcrumb
  const isTemplateId = offerId.startsWith('T-')
  let steps: Step[] = []

  if (!isCreatingOffer && !isCompletingDraft) {
    steps = [
      {
        id: OfferBreadcrumbStep.DETAILS,
        label: 'Détails de l’offre',
        url: `/offre/${offerId}/collectif/edition`,
      },
      {
        id: OfferBreadcrumbStep.STOCKS,
        label: 'Date et prix',
        url: useOfferStockEditionURL(true, offerId, false),
      },
      ...(!isTemplateId
        ? [
            {
              id: OfferBreadcrumbStep.VISIBILITY,
              label: 'Visibilité',
              url: `/offre/${offerId}/collectif/visibilite/edition`,
            },
          ]
        : []),
    ]
  } else {
    const stepList: { [key: string]: Step } = {
      [OfferBreadcrumbStep.DETAILS]: {
        id: OfferBreadcrumbStep.DETAILS,
        label: 'Détails de l’offre',
      },
      [OfferBreadcrumbStep.STOCKS]: {
        id: OfferBreadcrumbStep.STOCKS,
        label: 'Date et prix',
      },
      ...(!isTemplateId && {
        [OfferBreadcrumbStep.VISIBILITY]: {
          id: OfferBreadcrumbStep.VISIBILITY,
          label: 'Visibilité',
        },
      }),

      [OfferBreadcrumbStep.SUMMARY]: {
        id: OfferBreadcrumbStep.SUMMARY,
        label: 'Récapitulatif',
      },

      [OfferBreadcrumbStep.CONFIRMATION]: {
        id: OfferBreadcrumbStep.CONFIRMATION,
        label: 'Confirmation',
      },
    }
    let status = 'creation'
    if (isCompletingDraft) {
      status = 'brouillon'
    }

    if (offerId) {
      stepList[
        OfferBreadcrumbStep.DETAILS
      ].url = `/offre/${offerId}/individuel/${status}`

      stepList[
        OfferBreadcrumbStep.STOCKS
      ].url = `/offre/${offerId}/individuel/${status}/stocks`

      if (haveStock) {
        stepList[
          OfferBreadcrumbStep.SUMMARY
        ].url = `/offre/${offerId}/individuel/${status}/recapitulatif`
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
        isCreatingOffer || isCompletingDraft
          ? BreadcrumbStyle.DEFAULT
          : BreadcrumbStyle.TAB
      }
    />
  )
}

export default OfferBreadcrumb
