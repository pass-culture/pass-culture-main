import React, { useCallback, useEffect, useState } from 'react'
import { Route, Switch, useLocation, useParams } from 'react-router-dom'

import Spinner from 'components/layout/Spinner'
import { CollectiveOffer } from 'core/OfferEducational'
import getCollectiveOfferAdapter from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import CollectiveOfferLayout from 'new_components/CollectiveOfferLayout'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import CollectiveOfferEdition from 'routes/CollectiveOfferEdition'
import CollectiveOfferStockEdition from 'routes/CollectiveOfferStockEdition'
import CollectiveOfferSummary from 'routes/CollectiveOfferSummary'
import CollectiveOfferVisibility from 'routes/CollectiveOfferVisibility/CollectiveOfferEditionVisibility'

const CollectiveOfferEditionRoutes = (): JSX.Element => {
  const { offerId } = useParams<{ offerId: string }>()
  const location = useLocation()
  const [offer, setOffer] = useState<CollectiveOffer>()

  const loadCollectiveOffer = useCallback(async () => {
    const response = await getCollectiveOfferAdapter(offerId)
    if (response.isOk) {
      setOffer(response.payload)
    }
  }, [offerId])

  useEffect(() => {
    loadCollectiveOffer()
  }, [])

  if (!offer) {
    return <Spinner />
  }

  const getActiveStep = (pathname: string) => {
    if (pathname.includes('stocks')) {
      return OfferBreadcrumbStep.STOCKS
    }
    if (pathname.includes('visibilite')) {
      return OfferBreadcrumbStep.VISIBILITY
    }

    return OfferBreadcrumbStep.DETAILS
  }

  const isSummaryPage = location.pathname.includes('recapitulatif')

  return (
    <CollectiveOfferLayout
      title={isSummaryPage ? 'Récapitulatif' : 'Éditer une offre collective'}
      subTitle={offer.name}
      breadCrumpProps={
        isSummaryPage
          ? undefined
          : {
              activeStep: getActiveStep(location.pathname),
              offerId,
              isCreatingOffer: false,
            }
      }
    >
      <Switch>
        <Route path="/offre/:offerId([A-Z0-9]+)/collectif/edition">
          <CollectiveOfferEdition
            offer={offer}
            reloadCollectiveOffer={loadCollectiveOffer}
          />
        </Route>
        <Route path="/offre/:offerId([A-Z0-9]+)/collectif/stocks/edition">
          <CollectiveOfferStockEdition
            offer={offer}
            reloadCollectiveOffer={loadCollectiveOffer}
          />
        </Route>
        <Route path="/offre/:offerId([A-Z0-9]+)/collectif/visibilite/edition">
          <CollectiveOfferVisibility
            offer={offer}
            reloadCollectiveOffer={loadCollectiveOffer}
          />
        </Route>
        <Route path="/offre/:offerId([A-Z0-9]+)/collectif/recapitulatif">
          <CollectiveOfferSummary
            offer={offer}
            reloadCollectiveOffer={loadCollectiveOffer}
          />
        </Route>
      </Switch>
    </CollectiveOfferLayout>
  )
}

export default CollectiveOfferEditionRoutes
