import React from 'react'

import type { Step } from 'components/Breadcrumb'
import Breadcrumb, { BreadcrumbStyle } from 'components/Breadcrumb/Breadcrumb'
import { useOfferStockEditionURL } from 'hooks/useOfferEditionURL'

export enum CollectiveOfferBreadcrumbStep {
  DETAILS = 'details',
  STOCKS = 'stocks',
  VISIBILITY = 'visibility',
  SUMMARY = 'recapitulatif',
  CONFIRMATION = 'confirmation',
}

export interface OfferBreadcrumbProps {
  activeStep: CollectiveOfferBreadcrumbStep
  isCreatingOffer: boolean
  isCompletingDraft?: boolean
  offerId?: number
  isOfferEducational?: boolean
  className?: string
  isTemplate: boolean
  haveStock?: boolean
}

const CollectiveOfferBreadcrumb = ({
  activeStep,
  isCreatingOffer,
  isTemplate = false,
  isCompletingDraft = false,
  offerId = 0,
  className,
  haveStock = false,
}: OfferBreadcrumbProps): JSX.Element => {
  const stockEditionUrl = useOfferStockEditionURL(true, offerId, true)
  const isEditingExistingOffer = !(isCreatingOffer || isCompletingDraft)

  const stepList: { [key: string]: Step } = {}

  if (isEditingExistingOffer) {
    stepList[CollectiveOfferBreadcrumbStep.DETAILS] = {
      id: CollectiveOfferBreadcrumbStep.DETAILS,
      label: 'Détails de l’offre',
      url: `/offre/${offerId}/collectif/edition`,
    }
    if (!isTemplate) {
      stepList[CollectiveOfferBreadcrumbStep.STOCKS] = {
        id: CollectiveOfferBreadcrumbStep.STOCKS,
        label: 'Date et prix',
        url: stockEditionUrl,
      }
      stepList[CollectiveOfferBreadcrumbStep.VISIBILITY] = {
        id: CollectiveOfferBreadcrumbStep.VISIBILITY,
        label: 'Visibilité',
        url: `/offre/${offerId}/collectif/visibilite/edition`,
      }
    }
  } else {
    stepList[CollectiveOfferBreadcrumbStep.DETAILS] = {
      id: CollectiveOfferBreadcrumbStep.DETAILS,
      label: 'Détails de l’offre',
    }
    if (!isTemplate) {
      stepList[CollectiveOfferBreadcrumbStep.STOCKS] = {
        id: CollectiveOfferBreadcrumbStep.STOCKS,
        label: 'Date et prix',
        url: offerId ? `/offre/${offerId}/collectif/stocks` : '',
      }
      stepList[CollectiveOfferBreadcrumbStep.VISIBILITY] = {
        id: CollectiveOfferBreadcrumbStep.VISIBILITY,
        label: 'Visibilité',
        url:
          offerId && haveStock ? `/offre/${offerId}/collectif/visibilite` : '',
      }
    }
    stepList[CollectiveOfferBreadcrumbStep.SUMMARY] = {
      id: CollectiveOfferBreadcrumbStep.SUMMARY,
      label: 'Récapitulatif',
      url:
        offerId && haveStock
          ? `/offre/${offerId}/collectif/creation/recapitulatif`
          : '',
    }
    stepList[CollectiveOfferBreadcrumbStep.CONFIRMATION] = {
      id: CollectiveOfferBreadcrumbStep.CONFIRMATION,
      label: 'Confirmation',
    }

    // Add clickable urls depending on current completion
    // Switch fallthrough is intended, this is precisely the kind of use case for it
    /* eslint-disable no-fallthrough */
    switch (activeStep) {
      // @ts-expect-error switch fallthrough
      case CollectiveOfferBreadcrumbStep.CONFIRMATION:
        stepList[
          CollectiveOfferBreadcrumbStep.SUMMARY
        ].url = `/offre/${offerId}/collectif/creation/recapitulatif`

      // @ts-expect-error switch fallthrough
      case CollectiveOfferBreadcrumbStep.SUMMARY:
        if (!isTemplate) {
          stepList[
            CollectiveOfferBreadcrumbStep.VISIBILITY
          ].url = `/offre/${offerId}/collectif/visibilite`
        }

      // @ts-expect-error switch fallthrough
      case CollectiveOfferBreadcrumbStep.VISIBILITY:
        if (!isTemplate) {
          stepList[
            CollectiveOfferBreadcrumbStep.STOCKS
          ].url = `/offre/${offerId}/collectif/stocks`
        }

      case CollectiveOfferBreadcrumbStep.STOCKS:
        if (isTemplate) {
          stepList[
            CollectiveOfferBreadcrumbStep.DETAILS
          ].url = `/offre/collectif/vitrine/${offerId}/creation`
        } else {
          stepList[
            CollectiveOfferBreadcrumbStep.DETAILS
          ].url = `/offre/collectif/${offerId}/creation`
        }
    }
  }

  const steps = Object.values(stepList)

  return (
    <Breadcrumb
      activeStep={activeStep}
      className={className}
      steps={steps}
      styleType={
        isEditingExistingOffer ? BreadcrumbStyle.TAB : BreadcrumbStyle.STEPPER
      }
    />
  )
}

export default CollectiveOfferBreadcrumb
