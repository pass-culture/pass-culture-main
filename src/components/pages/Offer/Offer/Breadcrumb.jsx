import PropTypes from 'prop-types'
import React from 'react'

import Breadcrumb, { STYLE_TYPE_TAB, STYLE_TYPE_DEFAULT } from 'components/layout/Breadcrumb'

export const STEP_ID_DETAILS = 'details'
export const STEP_ID_STOCKS = 'stocks'

const OfferBreadcrumb = ({ activeStep, offer }) => {
  let steps
  if (offer) {
    steps = [
      {
        id: STEP_ID_DETAILS,
        label: "Détail de l'offre",
        url: `/offres/v2/${offer.id}/edition`,
      },
      {
        id: STEP_ID_STOCKS,
        label: 'Stock et prix',
        url: `/offres/v2/${offer.id}/stocks`,
      },
    ]
  } else {
    steps = [
      {
        id: STEP_ID_DETAILS,
        label: "Détail de l'offre",
        url: `/offres/v2/creation`,
      },
      {
        id: STEP_ID_STOCKS,
        label: 'Stock et prix',
      },
    ]
  }

  return (
    <Breadcrumb
      activeStep={activeStep}
      steps={steps}
      styleType={offer ? STYLE_TYPE_TAB : STYLE_TYPE_DEFAULT}
    />
  )
}

Breadcrumb.PropTypess = {
  offer: PropTypes.shape({
    id: PropTypes.string.isRequired,
  }).isRequired,
}

export default OfferBreadcrumb
