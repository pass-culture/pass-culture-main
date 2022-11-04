import React, { useCallback, useEffect, useState } from 'react'
import { Route, Switch, useLocation } from 'react-router-dom'

import { CollectiveOffer } from 'core/OfferEducational'
import getCollectiveOfferAdapter from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import CollectiveOfferLayout from 'new_components/CollectiveOfferLayout'
import CollectiveOfferEdition from 'pages/CollectiveOfferEdition'
import CollectiveOfferStockEdition from 'pages/CollectiveOfferStockEdition'
import CollectiveOfferSummaryEdition from 'pages/CollectiveOfferSummaryEdition'
import CollectiveOfferVisibility from 'pages/CollectiveOfferVisibility/CollectiveOfferEditionVisibility'
import Spinner from 'ui-kit/Spinner/Spinner'

import { getActiveStep } from '../utils/getActiveStep'

interface CollectiveOfferEditionRoutesProps {
  offerId: string
}

const CollectiveOfferEditionRoutes = ({
  offerId,
}: CollectiveOfferEditionRoutesProps): JSX.Element => {
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
        <Route path="/offre/:offerId/collectif/edition">
          <CollectiveOfferEdition
            offer={offer}
            reloadCollectiveOffer={loadCollectiveOffer}
          />
        </Route>
        <Route path="/offre/:offerId/collectif/stocks/edition">
          <CollectiveOfferStockEdition
            offer={offer}
            reloadCollectiveOffer={loadCollectiveOffer}
          />
        </Route>
        <Route path="/offre/:offerId/collectif/visibilite/edition">
          <CollectiveOfferVisibility
            offer={offer}
            reloadCollectiveOffer={loadCollectiveOffer}
          />
        </Route>
        <Route path="/offre/:offerId/collectif/recapitulatif">
          <CollectiveOfferSummaryEdition
            offer={offer}
            reloadCollectiveOffer={loadCollectiveOffer}
          />
        </Route>
      </Switch>
    </CollectiveOfferLayout>
  )
}

export default CollectiveOfferEditionRoutes
