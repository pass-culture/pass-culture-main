import PropTypes from 'prop-types'
import React from 'react'

import Breadcrumb, { STYLE_TYPE_TAB, STYLE_TYPE_DEFAULT } from 'components/layout/Breadcrumb'

export const STEP_ID_DETAILS = 'details'
export const STEP_ID_STOCKS = 'stocks'

const OfferBreadcrumb = ({ activeStep, isCreatingOffer, offerId }) => {
  let steps
  if (offerId) {
    steps = [
      {
        id: STEP_ID_DETAILS,
        label: "Détail de l'offre",
        url: `/offres/${offerId}/edition`,
      },
      {
        id: STEP_ID_STOCKS,
        label: 'Stock et prix',
        url: `/offres/${offerId}/stocks`,
      },
    ]
  } else {
    steps = [
      {
        id: STEP_ID_DETAILS,
        label: "Détail de l'offre",
        url: `/offres/creation`,
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
      styleType={isCreatingOffer ? STYLE_TYPE_DEFAULT : STYLE_TYPE_TAB}
    />
  )
}

Breadcrumb.defaultProps = {
  offerId: null,
}

Breadcrumb.PropTypess = {
  isCreatingOffer: PropTypes.bool.isRequired,
  offerId: PropTypes.string,
}

export default OfferBreadcrumb
