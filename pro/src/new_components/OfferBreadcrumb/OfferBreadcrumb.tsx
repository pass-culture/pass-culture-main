import React from 'react'

import useAnalytics from 'components/hooks/useAnalytics'
import { useOfferStockEditionURL } from 'components/hooks/useOfferEditionURL'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import type { Step } from 'new_components/Breadcrumb'
import Breadcrumb, {
  BreadcrumbStyle,
} from 'new_components/Breadcrumb/Breadcrumb'

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
  offerId?: string
  isOfferEducational?: boolean
  className?: string
  haveStock?: boolean
}

const OfferBreadcrumb = ({
  activeStep,
  isCreatingOffer,
  offerId = '',
  isOfferEducational = false,
  className,
  haveStock = false,
}: IOfferBreadcrumb): JSX.Element => {
  const { logEvent } = useAnalytics()
  const stockEditionUrl = useOfferStockEditionURL(isOfferEducational, offerId)

  const isTemplateId = offerId.startsWith('T-')
  let steps: Step[] = []

  if (activeStep == OfferBreadcrumbStep.CONFIRMATION && !isOfferEducational)
    return <></>
  if (
    !isCreatingOffer &&
    activeStep == OfferBreadcrumbStep.SUMMARY &&
    !isOfferEducational
  )
    return <></>

  if (!isCreatingOffer) {
    steps = [
      {
        id: OfferBreadcrumbStep.DETAILS,
        label: "Détails de l'offre",
        url: isOfferEducational
          ? `/offre/${offerId}/collectif/edition`
          : `/offre/${offerId}/individuel/edition`,
      },
      {
        id: OfferBreadcrumbStep.STOCKS,
        label: isOfferEducational ? 'Date et prix' : 'Stocks et prix',
        url: stockEditionUrl,
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
        label: "Détails de l'offre",
      },
      [OfferBreadcrumbStep.STOCKS]: {
        id: OfferBreadcrumbStep.STOCKS,
        label: isOfferEducational ? 'Date et prix' : 'Stocks et prix',
      },
      ...(isOfferEducational
        ? {
            [OfferBreadcrumbStep.VISIBILITY]: {
              id: OfferBreadcrumbStep.VISIBILITY,
              label: 'Visibilité',
            },
          }
        : {
            [OfferBreadcrumbStep.SUMMARY]: {
              id: OfferBreadcrumbStep.SUMMARY,
              label: 'Récapitulatif',
            },
          }),
      [OfferBreadcrumbStep.CONFIRMATION]: {
        id: OfferBreadcrumbStep.CONFIRMATION,
        label: 'Confirmation',
      },
    }

    if (offerId) {
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
    }

    steps = Object.values(stepList)
  }

  // Add firebase tracking only on individual offers
  if (!isOfferEducational)
    steps.map((step, index) => {
      steps[index].onClick = () => {
        logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
          from: activeStep,
          to: step.id,
          used: OFFER_FORM_NAVIGATION_MEDIUM.BREADCRUMB,
          isEdition: !isCreatingOffer,
        })
      }
    })

  return (
    <Breadcrumb
      activeStep={activeStep}
      className={className}
      steps={steps}
      styleType={
        isCreatingOffer
          ? isOfferEducational
            ? BreadcrumbStyle.DEFAULT
            : BreadcrumbStyle.STEPPER
          : BreadcrumbStyle.TAB
      }
    />
  )
}

export default OfferBreadcrumb
