/*
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'
import { Route, Switch } from 'react-router-dom'

import Titles from 'components/layout/Titles/Titles'
import Breadcrumb, {
  STEP_ID_CONFIRMATION,
  STEP_ID_DETAILS,
  STEP_ID_STOCKS,
} from 'components/pages/Offers/Offer/Breadcrumb'
import ConfirmationContainer from 'components/pages/Offers/Offer/Confirmation/ConfirmationContainer'
import LeavingOfferCreationDialog from 'components/pages/Offers/Offer/LeavingOfferCreationDialog/LeavingOfferCreationDialog'
import OfferDetailsContainer from 'components/pages/Offers/Offer/OfferDetails/OfferDetailsContainer'
import { OfferHeader } from 'components/pages/Offers/Offer/OfferStatus/OfferHeader'
import StocksContainer from 'components/pages/Offers/Offer/Stocks/StocksContainer'
import { OFFER_STATUS_DRAFT } from 'components/pages/Offers/Offers/_constants'
import * as pcapi from 'repository/pcapi/pcapi'

const mapPathToStep = {
  creation: STEP_ID_DETAILS,
  edition: STEP_ID_DETAILS,
  stocks: STEP_ID_STOCKS,
  confirmation: STEP_ID_CONFIRMATION,
}

const OfferLayout = ({ location, match }) => {
  const [offer, setOffer] = useState(null)
  const [isCreatingOffer, setIsCreatingOffer] = useState(true)

  const loadOffer = useCallback(
    async (offerId, creationMode = false) => {

      const existingOffer = await pcapi.loadOffer(offerId)
      setOffer(existingOffer)
      setIsCreatingOffer(creationMode || existingOffer.status === OFFER_STATUS_DRAFT)
    },
    [setOffer]
  )

  const reloadOffer = useCallback(
    async (creationMode = false) => (offer.id ? await loadOffer(offer.id, creationMode) : false),
    [loadOffer, offer?.id]
  )

  const shouldBlockNavigation = useCallback(
    nextLocation => {
      const offerCreationPath = '/offres/creation'
      const stocksPathRegex = /\/offres\/([A-Z0-9]+)\/stocks/g
      const confirmationPathRegex = /\/offres\/([A-Z0-9]+)\/confirmation/g

      if (
        (location.pathname.match(stocksPathRegex) &&
          nextLocation.pathname.startsWith(offerCreationPath)) ||
        (location.pathname.match(offerCreationPath) &&
          nextLocation.pathname.match(confirmationPathRegex))
      ) {
        nextLocation.pathname = '/offres'
        nextLocation.search = ''
        return true
      }
      if (location.pathname.match(confirmationPathRegex)) {
        if (nextLocation.pathname.match(stocksPathRegex)) {
          nextLocation.pathname = '/offres'
          nextLocation.search = ''
        }
        return false
      }
      if (
        nextLocation.pathname.match(stocksPathRegex) ||
        nextLocation.pathname.match(confirmationPathRegex) ||
        (location.pathname.startsWith(offerCreationPath) &&
          nextLocation.pathname.startsWith(offerCreationPath))
      ) {
        return false
      }
      return true
    },
    [location]
  )

  useEffect(() => {
    async function loadOfferFromQueryParam () {
      await loadOffer(match.params.offerId)
    }
    match.params.offerId && loadOfferFromQueryParam()
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

  const offerHeader =
    !isCreatingOffer && !location.pathname.includes('/confirmation') ? (
      <OfferHeader
        offer={offer}
        reloadOffer={reloadOffer}
      />
    ) : null

  return (
    <div className="offer-page">
      <Titles
        action={offerHeader}
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
              location={location}
              offer={offer}
              reloadOffer={reloadOffer}
            />
          </Route>
          <Route
            exact
            path={`${match.url}/confirmation`}
          >
            <ConfirmationContainer
              isCreatingOffer={isCreatingOffer}
              location={location}
              offer={offer}
              setOffer={setOffer}
            />
          </Route>
        </Switch>
      </div>
      <LeavingOfferCreationDialog
        shouldBlockNavigation={shouldBlockNavigation}
        when={isCreatingOffer}
      />
    </div>
  )
}

OfferLayout.propTypes = {
  location: PropTypes.shape().isRequired,
  match: PropTypes.shape().isRequired,
}

export default OfferLayout
