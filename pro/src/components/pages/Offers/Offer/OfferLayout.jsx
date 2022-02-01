/*
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import PropTypes from 'prop-types'
import React, { useCallback, useEffect, useState } from 'react'
import { Route, Switch, useHistory } from 'react-router-dom'

import Titles from 'components/layout/Titles/Titles'
import ConfirmationContainer from 'components/pages/Offers/Offer/Confirmation/ConfirmationContainer'
import { OfferHeader } from 'components/pages/Offers/Offer/OfferStatus/OfferHeader'
import StocksContainer from 'components/pages/Offers/Offer/Stocks/StocksContainer'
import { OFFER_STATUS_DRAFT } from 'components/pages/Offers/Offers/_constants'
import Breadcrumb, { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import RouteLeavingGuardOfferCreation from 'new_components/RouteLeavingGuardOfferCreation'
import * as pcapi from 'repository/pcapi/pcapi'

import OfferDetails from './OfferDetails'

const mapPathToStep = {
  creation: OfferBreadcrumbStep.DETAILS,
  edition: OfferBreadcrumbStep.DETAILS,
  stocks: OfferBreadcrumbStep.STOCKS,
  confirmation: OfferBreadcrumbStep.CONFIRMATION,
}

const OfferLayout = ({ location, match }) => {
  const history = useHistory()

  const [offer, setOffer] = useState(null)
  const [isCreatingOffer, setIsCreatingOffer] = useState(true)

  const loadOffer = useCallback(
    async (offerId, creationMode = false) => {
      const existingOffer = await pcapi.loadOffer(offerId)

      setOffer(existingOffer)
      setIsCreatingOffer(
        creationMode || existingOffer.status === OFFER_STATUS_DRAFT
      )
    },
    [setOffer]
  )

  const stepName = location.pathname.match(/[a-z]+$/)
  const activeStep = stepName ? mapPathToStep[stepName[0]] : null

  const reloadOffer = useCallback(
    async (creationMode = false) =>
      offer.id ? await loadOffer(offer.id, creationMode) : false,
    [loadOffer, offer?.id]
  )

  useEffect(() => {
    async function loadOfferFromQueryParam() {
      await loadOffer(match.params.offerId)
    }
    match.params.offerId && loadOfferFromQueryParam()
  }, [loadOffer, match.params.offerId])

  let pageTitle = 'Nouvelle offre'

  if (match.params.offerId && !offer) {
    return null
  }

  if (!isCreatingOffer) {
    pageTitle = 'Éditer une offre'
  }

  const offerHeader =
    !isCreatingOffer && !location.pathname.includes('/confirmation') ? (
      <OfferHeader offer={offer} reloadOffer={reloadOffer} />
    ) : null

  if (offer?.isEducational) {
    history.push(
      `/offre/${match.params.offerId}/scolaire/${
        activeStep === 'stocks' ? 'stocks/edition' : 'edition'
      }`
    )
  }

  return (
    <div className="offer-page">
      <Titles action={offerHeader} title={pageTitle} />

      <Breadcrumb
        activeStep={activeStep}
        isCreatingOffer={isCreatingOffer}
        isOfferEducational={offer?.isEducational}
        offerId={offer?.id}
      />

      <div className="offer-content">
        <Switch>
          <Route exact path="/offre/creation/individuel">
            {/* FIXME (cgaunet, 2022-01-31) This is a quick win to fix a flaky E2E test */}
            {/* There is a concurrency run between the RouteLeavingGuardOfferCreation and the reloadOffer call */}
            {/* in OfferDetails as the offer is loaded in the stock edition page */}
            <OfferDetails offer={offer} reloadOffer={reloadOffer} />
          </Route>
          <Route exact path={`${match.url}/edition`}>
            <OfferDetails offer={offer} reloadOffer={reloadOffer} />
          </Route>
          <Route exact path={`${match.url}/stocks`}>
            <StocksContainer
              location={location}
              offer={offer}
              reloadOffer={reloadOffer}
            />
          </Route>
          <Route exact path={`${match.url}/confirmation`}>
            <ConfirmationContainer
              isCreatingOffer={isCreatingOffer}
              location={location}
              offer={offer}
              setOffer={setOffer}
            />
          </Route>
        </Switch>
      </div>
      <RouteLeavingGuardOfferCreation when={isCreatingOffer} />
    </div>
  )
}

OfferLayout.propTypes = {
  location: PropTypes.shape().isRequired,
  match: PropTypes.shape().isRequired,
}

export default OfferLayout
