import Breadcrumb, {
  BreadcrumbStyle,
} from 'new_components/Breadcrumb/Breadcrumb'
import {
  useOfferEditionURL,
  useOfferStockEditionURL,
} from 'components/hooks/useOfferEditionURL'

import React from 'react'
import useActiveFeature from 'components/hooks/useActiveFeature'

export enum OfferBreadcrumbStep {
  DETAILS = 'details',
  STOCKS = 'stocks',
  VISIBILITY = 'visibility',
  CONFIRMATION = 'confirmation',
}

interface IOfferBreadcrumb {
  activeStep: OfferBreadcrumbStep
  isCreatingOffer: boolean
  offerId?: string
  isOfferEducational?: boolean
  className?: string
}

const OfferBreadcrumb = ({
  activeStep,
  isCreatingOffer,
  offerId = '',
  isOfferEducational = false,
  className,
}: IOfferBreadcrumb): JSX.Element => {
  const enableEducationalInstitutionAssociation = useActiveFeature(
    'ENABLE_EDUCATIONAL_INSTITUTION_ASSOCIATION'
  )
  const offerEditionUrl = useOfferEditionURL(isOfferEducational, offerId)
  const stockEditionUrl = useOfferStockEditionURL(isOfferEducational, offerId)

  let steps = []

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
      ...(isOfferEducational && enableEducationalInstitutionAssociation
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
    steps = [
      {
        id: OfferBreadcrumbStep.DETAILS,
        label: "Détails de l'offre",
      },
      {
        id: OfferBreadcrumbStep.STOCKS,
        label: isOfferEducational ? 'Date et prix' : 'Stock et prix',
      },
      ...(isOfferEducational && enableEducationalInstitutionAssociation
        ? [
            {
              id: OfferBreadcrumbStep.VISIBILITY,
              label: 'Visibilité',
            },
          ]
        : []),
      {
        id: OfferBreadcrumbStep.CONFIRMATION,
        label: 'Confirmation',
      },
    ]
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
