import React from 'react'

import type { Step } from 'components/Breadcrumb'
import Breadcrumb, { BreadcrumbStyle } from 'components/Breadcrumb/Breadcrumb'
import useActiveFeature from 'hooks/useActiveFeature'
import { useOfferStockEditionURL } from 'hooks/useOfferEditionURL'

export enum CollectiveOfferBreadcrumbStep {
  DETAILS = 'details',
  STOCKS = 'stocks',
  VISIBILITY = 'visibility',
  SUMMARY = 'recapitulatif',
  CONFIRMATION = 'confirmation',
}

export interface IOfferBreadcrumb {
  activeStep: CollectiveOfferBreadcrumbStep
  isCreatingOffer: boolean
  isCompletingDraft?: boolean
  offerId?: string
  isOfferEducational?: boolean
  className?: string
  isTemplate: boolean
}

const CollectiveOfferBreadcrumb = ({
  activeStep,
  isCreatingOffer,
  isTemplate = false,
  isCompletingDraft = false,
  offerId = '',
  className,
}: IOfferBreadcrumb): JSX.Element => {
  const isOfferFormV3 = useActiveFeature('OFFER_FORM_V3')
  const stockEditionUrl = useOfferStockEditionURL(true, offerId, isOfferFormV3)
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
      }
      stepList[CollectiveOfferBreadcrumbStep.VISIBILITY] = {
        id: CollectiveOfferBreadcrumbStep.VISIBILITY,
        label: 'Visibilité',
      }
    }
    stepList[CollectiveOfferBreadcrumbStep.SUMMARY] = {
      id: CollectiveOfferBreadcrumbStep.SUMMARY,
      label: 'Récapitulatif',
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
