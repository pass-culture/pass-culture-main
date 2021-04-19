import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'
import { Route, Switch } from 'react-router-dom'

import Titles from 'components/layout/Titles/Titles'
import Breadcrumb, {
  STEP_ID_DETAILS,
  STEP_ID_STOCKS,
} from 'components/pages/Offers/Offer/Breadcrumb'
import OfferDetailsContainer from 'components/pages/Offers/Offer/OfferDetails/OfferDetailsContainer'
import { OfferHeader } from 'components/pages/Offers/Offer/OfferStatus/OfferHeader'
import StocksContainer from 'components/pages/Offers/Offer/Stocks/StocksContainer'
import { OFFER_STATUS_DRAFT } from 'components/pages/Offers/Offers/_constants'
import * as pcapi from 'repository/pcapi/pcapi'

import LeavingOfferCreationDialog from './LeavingOfferCreationDialog/LeavingOfferCreationDialog'

const mapPathToStep = {
  creation: STEP_ID_DETAILS,
  edition: STEP_ID_DETAILS,
  stocks: STEP_ID_STOCKS,
}

const OfferLayout = props => {
  const { location, match } = props

  const [offer, setOffer] = useState(null)
  const [isCreatingOffer, setIsCreatingOffer] = useState(true)

  const loadOffer = useCallback(
    async offerId => {
      const existingOffer = await pcapi.loadOffer(offerId)
      setOffer(existingOffer)
      setIsCreatingOffer(existingOffer.status === OFFER_STATUS_DRAFT)
    },
    [setOffer]
  )

  const reloadOffer = useCallback(async () => (offer.id ? loadOffer(offer.id) : false), [
    loadOffer,
    offer,
  ])

  const shouldBlockNavigation = useCallback(
    nextLocation => {
      const stocksPathRegex = /\/offres\/([A-Z0-9]+)\/stocks/g
      if (isCreatingOffer && nextLocation.pathname.match(stocksPathRegex)) {
        return false
      }
      return true
    },
    [isCreatingOffer]
  )

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

  if (!isCreatingOffer) {
    pageTitle = 'Éditer une offre'
  }

  const offerStatus =
    offer?.status && offer?.status !== OFFER_STATUS_DRAFT ? (
      <OfferHeader
        offer={offer}
        reloadOffer={reloadOffer}
      />
    ) : null

  return (
    <div className="offer-page">
      <Titles
        action={offerStatus}
        title={pageTitle}
      />

      <Breadcrumb
        activeStep={activeStep}
        isCreatingOffer={isCreatingOffer}
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
      <LeavingOfferCreationDialog
        shouldBlockNavigation={shouldBlockNavigation}
        when={isCreatingOffer || offer.status === OFFER_STATUS_DRAFT}
      />
    </div>
  )
}

OfferLayout.propTypes = {
  location: PropTypes.shape().isRequired,
  match: PropTypes.shape().isRequired,
}

export default OfferLayout
