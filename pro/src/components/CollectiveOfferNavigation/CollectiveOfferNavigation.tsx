import React from 'react'

import Stepper from 'components/Stepper'
import { Step } from 'components/Stepper/Stepper'
import { useOfferStockEditionURL } from 'hooks/useOfferEditionURL'
import Tabs from 'ui-kit/Tabs'

export enum CollectiveOfferStep {
  DETAILS = 'details',
  STOCKS = 'stocks',
  VISIBILITY = 'visibility',
  SUMMARY = 'recapitulatif',
  CONFIRMATION = 'confirmation',
  PREVIEW = 'preview',
}

export interface CollectiveOfferNavigationProps {
  activeStep: CollectiveOfferStep
  isCreatingOffer: boolean
  isCompletingDraft?: boolean
  offerId?: number
  isOfferEducational?: boolean
  className?: string
  isTemplate: boolean
  haveStock?: boolean
  requestId?: string | null
}

const CollectiveOfferNavigation = ({
  activeStep,
  isCreatingOffer,
  isTemplate = false,
  isCompletingDraft = false,
  offerId = 0,
  className,
  haveStock = false,
  requestId = null,
}: CollectiveOfferNavigationProps): JSX.Element => {
  const stockEditionUrl = useOfferStockEditionURL(true, offerId)
  const isEditingExistingOffer = !(isCreatingOffer || isCompletingDraft)

  const stepList: { [key: string]: Step } = {}

  const requestIdUrl = requestId ? `?requete=${requestId}` : ''

  if (isEditingExistingOffer) {
    if (!isTemplate) {
      stepList[CollectiveOfferStep.DETAILS] = {
        id: CollectiveOfferStep.DETAILS,
        label: 'Détails de l’offre',
        url: `/offre/${offerId}/collectif/edition`,
      }
      stepList[CollectiveOfferStep.STOCKS] = {
        id: CollectiveOfferStep.STOCKS,
        label: 'Date et prix',
        url: stockEditionUrl,
      }
      stepList[CollectiveOfferStep.VISIBILITY] = {
        id: CollectiveOfferStep.VISIBILITY,
        label: 'Établissement et enseignant',
        url: `/offre/${offerId}/collectif/visibilite/edition`,
      }
    }
  } else {
    stepList[CollectiveOfferStep.DETAILS] = {
      id: CollectiveOfferStep.DETAILS,
      label: 'Détails de l’offre',
    }
    if (!isTemplate) {
      stepList[CollectiveOfferStep.STOCKS] = {
        id: CollectiveOfferStep.STOCKS,
        label: 'Date et prix',
        url: offerId ? `/offre/${offerId}/collectif/stocks${requestIdUrl}` : '',
      }
      stepList[CollectiveOfferStep.VISIBILITY] = {
        id: CollectiveOfferStep.VISIBILITY,
        label: 'Établissement et enseignant',
        url:
          offerId && haveStock
            ? `/offre/${offerId}/collectif/visibilite${requestIdUrl}`
            : '',
      }
    }
    stepList[CollectiveOfferStep.SUMMARY] = {
      id: CollectiveOfferStep.SUMMARY,
      label: 'Récapitulatif',
      url:
        offerId && haveStock
          ? `/offre/${offerId}/collectif/creation/recapitulatif`
          : offerId
            ? `/offre/${offerId}/collectif/vitrine/creation/recapitulatif`
            : ``,
    }
    if (isTemplate) {
      stepList[CollectiveOfferStep.PREVIEW] = {
        id: CollectiveOfferStep.PREVIEW,
        label: 'Aperçu',
        url:
          offerId && haveStock
            ? `/offre/${offerId}/collectif/vitrine/creation/apercu`
            : '',
      }
    }
    stepList[CollectiveOfferStep.CONFIRMATION] = {
      id: CollectiveOfferStep.CONFIRMATION,
      label: 'Confirmation',
    }

    // Add clickable urls depending on current completion
    // Switch fallthrough is intended, this is precisely the kind of use case for it
    /* eslint-disable no-fallthrough */
    switch (activeStep) {
      // @ts-expect-error switch fallthrough
      case CollectiveOfferStep.CONFIRMATION:
        stepList[CollectiveOfferStep.SUMMARY].url =
          `/offre/${offerId}/collectif/creation/recapitulatif`

      // @ts-expect-error switch fallthrough
      case CollectiveOfferStep.SUMMARY:
        if (!isTemplate) {
          stepList[CollectiveOfferStep.VISIBILITY].url =
            `/offre/${offerId}/collectif/visibilite`
        }

      // @ts-expect-error switch fallthrough
      case CollectiveOfferStep.VISIBILITY:
        if (!isTemplate) {
          stepList[CollectiveOfferStep.STOCKS].url =
            `/offre/${offerId}/collectif/stocks`
        }

      // @ts-expect-error switch fallthrough
      case CollectiveOfferStep.PREVIEW:
        if (isTemplate) {
          stepList[CollectiveOfferStep.PREVIEW].url =
            `/offre/${offerId}/collectif/vitrine/creation/apercu`
        }

      // @ts-expect-error switch fallthrough
      case CollectiveOfferStep.STOCKS:
        if (isTemplate) {
          stepList[CollectiveOfferStep.DETAILS].url =
            `/offre/collectif/vitrine/${offerId}/creation`
        } else {
          stepList[CollectiveOfferStep.DETAILS].url =
            `/offre/collectif/${offerId}/creation${requestIdUrl}`
        }

      case CollectiveOfferStep.DETAILS:
      // Nothing to do here
    }
  }

  const steps = Object.values(stepList)
  const tabs = steps.map(({ id, label, url }) => ({
    key: id,
    label,
    url,
  }))

  return isEditingExistingOffer ? (
    <Tabs tabs={tabs} selectedKey={activeStep} />
  ) : (
    <Stepper activeStep={activeStep} className={className} steps={steps} />
  )
}

export default CollectiveOfferNavigation
