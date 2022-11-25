import React from 'react'

import type { Step } from 'components/Breadcrumb'
import Breadcrumb, { BreadcrumbStyle } from 'components/Breadcrumb/Breadcrumb'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
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
  isOfferEducational?: boolean
  className?: string
  haveStock?: boolean
}

const OfferBreadcrumb = ({
  activeStep,
  isCreatingOffer,
  isCompletingDraft = false,
  offerId = '',
  isOfferEducational = false,
  className,
  haveStock = false,
}: IOfferBreadcrumb): JSX.Element => {
  const { logEvent } = useAnalytics()
  // it is never OfferFormV3 in this breadcrumb
  const isOfferFormV3 = false
  const isTemplateId = offerId.startsWith('T-')
  let steps: Step[] = []

  if (activeStep == OfferBreadcrumbStep.CONFIRMATION && !isOfferEducational) {
    return <></>
  }
  if (
    !isCreatingOffer &&
    activeStep == OfferBreadcrumbStep.SUMMARY &&
    !isOfferEducational &&
    !isCompletingDraft
  ) {
    return <></>
  }

  if (!isCreatingOffer && !isCompletingDraft) {
    steps = [
      {
        id: OfferBreadcrumbStep.DETAILS,
        label: 'Détails de l’offre',
        url: isOfferEducational
          ? `/offre/${offerId}/collectif/edition`
          : `/offre/${offerId}/individuel/edition`,
      },
      {
        id: OfferBreadcrumbStep.STOCKS,
        label: isOfferEducational ? 'Date et prix' : 'Stocks et prix',
        url: useOfferStockEditionURL(
          isOfferEducational,
          offerId,
          isOfferFormV3
        ),
      },
      ...(isOfferEducational && !isTemplateId
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
        label: isOfferEducational ? 'Date et prix' : 'Stocks et prix',
      },
      ...(isOfferEducational &&
        !isTemplateId && {
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

  // Add firebase tracking only on individual offers
  if (!isOfferEducational) {
    steps.map((step, index) => {
      steps[index].onClick = () => {
        logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
          from: activeStep,
          to: step.id,
          used: OFFER_FORM_NAVIGATION_MEDIUM.BREADCRUMB,
          isEdition: !isCreatingOffer,
          isDraft: isCreatingOffer || isCompletingDraft,
          offerId: offerId,
        })
      }
    })
  }

  return (
    <Breadcrumb
      activeStep={activeStep}
      className={className}
      steps={steps}
      styleType={
        isCreatingOffer || isCompletingDraft
          ? isOfferEducational
            ? BreadcrumbStyle.DEFAULT
            : BreadcrumbStyle.STEPPER
          : BreadcrumbStyle.TAB
      }
    />
  )
}

export default OfferBreadcrumb
