import PropTypes from 'prop-types'
import React from 'react'

import Breadcrumb, { STYLE_TYPE_TAB, STYLE_TYPE_DEFAULT } from 'components/layout/Breadcrumb'

export const STEP_ID_DETAILS = 'details'
export const STEP_ID_STOCKS = 'stocks'
export const STEP_ID_CONFIRMATION = 'confirmation'

const OfferBreadcrumb = ({ activeStep, isCreatingOffer, isOfferCreationFinished, offerId }) => {
  let steps = []

  if (offerId) {
    steps = [
      {
        id: STEP_ID_DETAILS,
        label: "Détail de l'offre",
        url: isCreatingOffer ? null : `/offres/${offerId}/edition`,
      },
      {
        id: STEP_ID_STOCKS,
        label: 'Stock et prix',
        url: isCreatingOffer ? null : `/offres/${offerId}/stocks`,
      },
    ]

    if (!isOfferCreationFinished) {
      steps.push({
        id: STEP_ID_CONFIRMATION,
        label: 'Confirmation',
      })
    }
  } else {
    steps = [
      {
        id: STEP_ID_DETAILS,
        label: "Détail de l'offre",
      },
      {
        id: STEP_ID_STOCKS,
        label: 'Stock et prix',
      },
      {
        id: STEP_ID_CONFIRMATION,
        label: 'Confirmation',
      },
    ]
  }

  return (
    <Breadcrumb
      activeStep={activeStep}
      steps={steps}
      styleType={isCreatingOffer ? STYLE_TYPE_DEFAULT : STYLE_TYPE_TAB}
    />
  )
}

OfferBreadcrumb.defaultProps = {
  isOfferCreationFinished: true,
  offerId: null,
}

OfferBreadcrumb.propTypes = {
  activeStep: PropTypes.string.isRequired,
  isCreatingOffer: PropTypes.bool.isRequired,
  isOfferCreationFinished: PropTypes.bool,
  offerId: PropTypes.string,
}

export default OfferBreadcrumb
