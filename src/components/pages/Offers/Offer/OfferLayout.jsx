import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState, useRef } from 'react'
import { Switch, Route } from 'react-router-dom'

import Titles from 'components/layout/Titles/Titles'
import Breadcrumb, {
  STEP_ID_DETAILS,
  STEP_ID_STOCKS,
} from 'components/pages/Offers/Offer/Breadcrumb'
import OfferDetailsContainer from 'components/pages/Offers/Offer/OfferDetails/OfferDetailsContainer'
import OfferStatus from 'components/pages/Offers/Offer/OfferStatus/OfferStatus'
import StocksContainer from 'components/pages/Offers/Offer/Stocks/StocksContainer'
import * as pcapi from 'repository/pcapi/pcapi'

const mapPathToStep = {
  creation: STEP_ID_DETAILS,
  edition: STEP_ID_DETAILS,
  stocks: STEP_ID_STOCKS,
}

const OfferLayout = props => {
  const { location, match } = props

  const isCreatingOffer = useRef(!match.params.offerId)
  const [offer, setOffer] = useState(null)

  const loadOffer = useCallback(
    async offerId => {
      const existingOffer = await pcapi.loadOffer(offerId)
      setOffer(existingOffer)
    },
    [setOffer]
  )

  const reloadOffer = useCallback(async () => (offer.id ? loadOffer(offer.id) : false), [
    loadOffer,
    offer,
  ])

  useEffect(() => {
    if (match.params.offerId) {
      loadOffer(match.params.offerId)
    }
  }, [loadOffer, match.params.offerId])

  const stepName = location.pathname.match(/[a-z]+$/)
  const activeStep = stepName ? mapPathToStep[stepName[0]] : null

  let pageTitle = 'Nouvelle offre'

  if (match.params.offerId && !offer) {
    return null
  }

  if (!isCreatingOffer.current) {
    pageTitle = 'Éditer une offre'
  }

  const offerStatus =
    offer?.status && offer?.stocks.length > 0 ? <OfferStatus status={offer.status} /> : null

  return (
    <div className="offer-page">
      <Titles
        action={offerStatus}
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
            path="/offres/creation"
          >
            <OfferDetailsContainer offer={offer} />
          </Route>
          <Route
            exact
            path={`${match.url}/edition`}
          >
            <OfferDetailsContainer
              offer={offer}
              reloadOffer={reloadOffer}
            />
          </Route>
          <Route
            exact
            path={`${match.url}/stocks`}
          >
            <StocksContainer
              offer={offer}
              reloadOffer={reloadOffer}
            />
          </Route>
        </Switch>
      </div>
    </div>
  )
}

OfferLayout.propTypes = {
  location: PropTypes.shape().isRequired,
  match: PropTypes.shape().isRequired,
}

export default OfferLayout
