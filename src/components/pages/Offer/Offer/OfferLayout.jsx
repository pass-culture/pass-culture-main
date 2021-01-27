import React, { useEffect, useState, useRef } from 'react'
import { Switch, Route } from 'react-router-dom'

import Titles from 'components/layout/Titles/Titles'
import OfferDetailsContainer from 'components/pages/Offer/Offer/OfferDetails/OfferDetailsContainer'
import StocksContainer from 'components/pages/Offer/Offer/Stocks/StocksContainer'
import * as pcapi from 'repository/pcapi/pcapi'

import Breadcrumb, { STEP_ID_DETAILS, STEP_ID_STOCKS } from './Breadcrumb'
import OfferPreviewLink from './OfferPreviewLink/OfferPreviewLink'

const mapPathToStep = {
  creation: STEP_ID_DETAILS,
  edition: STEP_ID_DETAILS,
  stocks: STEP_ID_STOCKS,
}

const OfferLayout = props => {
  const { location, match } = props

  const isCreatingOffer = useRef(!match.params.offerId)
  const [offer, setOffer] = useState(null)

  useEffect(() => {
    async function loadOffer(offerId) {
      const existingOffer = await pcapi.loadOffer(offerId)
      setOffer(existingOffer)
    }

    if (match.params.offerId) {
      loadOffer(match.params.offerId)
    }
  }, [match.params.offerId])

  const stepName = location.pathname.match(/[a-z]+$/)
  const activeStep = stepName ? mapPathToStep[stepName[0]] : null

  let pageTitle = 'Nouvelle offre'
  let actionLink

  if (match.params.offerId && !offer) {
    return null
  }

  if (!isCreatingOffer.current) {
    pageTitle = 'Éditer une offre'
    const mediationId = offer.activeMediation ? offer.activeMediation.id : null
    actionLink = (
      <OfferPreviewLink
        mediationId={mediationId}
        offerId={offer.id}
      />
    )
  }

  return (
    <div className="offer-page-v2">
      <Titles
        action={actionLink}
        title={pageTitle}
      />

      <Breadcrumb
        activeStep={activeStep}
        isCreatingOffer={isCreatingOffer.current}
        offerId={offer?.id}
      />

      <div className="offer-content">
        <Switch>
          <Route
            exact
            path="/offres/v2/creation"
          >
            <OfferDetailsContainer offer={offer} />
          </Route>
          <Route
            exact
            path={`${match.url}/edition`}
          >
            <OfferDetailsContainer offer={offer} />
          </Route>
          <Route
            exact
            path={`${match.url}/stocks`}
          >
            <StocksContainer offer={offer} />
          </Route>
        </Switch>
      </div>
    </div>
  )
}

export default OfferLayout
