import React, { useEffect, useState } from 'react'
import { Route, Switch, useParams } from 'react-router-dom'

import { LogRouteNavigation } from 'app/AppRouter/LogRouteNavigation'
import CollectiveOfferLayout from 'components/CollectiveOfferLayout'
import { CollectiveOffer } from 'core/OfferEducational'
import getCollectiveOfferAdapter from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import CollectiveOfferConfirmation from 'pages/CollectiveOfferConfirmation'
import CollectiveOfferCreationFromTemplate from 'pages/CollectiveOfferCreationFromTemplate'
import CollectiveOfferStockCreationFromTemplate from 'pages/CollectiveOfferStockCreationFromTemplate'
import CollectiveOfferSummaryCreation from 'pages/CollectiveOfferSummaryCreation'
import CollectiveOfferCreationVisibility from 'pages/CollectiveOfferVisibility/CollectiveOfferCreationVisibility'
import Spinner from 'ui-kit/Spinner/Spinner'

import { getActiveStep } from '../utils/getActiveStep'

const CollectiveOfferCreationRoutes = (): JSX.Element => {
  const { offerId } = useParams<{
    offerId?: string
    templateId?: string
  }>()
  const [collectiveOffer, setCollectiveOffer] = useState<CollectiveOffer>()

  useEffect(() => {
    const loadCollectiveOffer = async (offerId: string) => {
      const response = await getCollectiveOfferAdapter(offerId)
      if (response.isOk) {
        setCollectiveOffer(response.payload)
      }
    }

    if (offerId) {
      loadCollectiveOffer(offerId)
    }
  }, [offerId])

  return (
    <Switch>
      <Route path="/offre/duplication/collectif/:offerId/confirmation">
        <LogRouteNavigation
          route={{ title: 'Offre collective - duplication - confirmation' }}
        >
          {collectiveOffer ? (
            <CollectiveOfferConfirmation offer={collectiveOffer} />
          ) : (
            <Spinner />
          )}
        </LogRouteNavigation>
      </Route>
      <CollectiveOfferLayout
        title="Créer une offre pour un établissement scolaire"
        subTitle={collectiveOffer?.name}
        breadCrumpProps={{
          activeStep: getActiveStep(location.pathname),
          isCreatingOffer: true,
          offerId,
        }}
      >
        <Route path="/offre/duplication/collectif/:templateId" exact>
          <LogRouteNavigation
            route={{ title: 'Offre collective - duplication - création' }}
          >
            <CollectiveOfferCreationFromTemplate />
          </LogRouteNavigation>
        </Route>
        <Route path="/offre/duplication/collectif/:offerId/stocks">
          {collectiveOffer ? (
            <CollectiveOfferStockCreationFromTemplate offer={collectiveOffer} />
          ) : (
            <Spinner />
          )}
        </Route>
        <Route path="/offre/duplication/collectif/:offerId/visibilite">
          <LogRouteNavigation
            route={{ title: 'Offre collective - duplication - visibilité' }}
          >
            {collectiveOffer ? (
              <CollectiveOfferCreationVisibility
                setOffer={setCollectiveOffer}
                offer={collectiveOffer}
                isDuplicatingOffer
              />
            ) : (
              <Spinner />
            )}
          </LogRouteNavigation>
        </Route>
        <Route path="/offre/duplication/collectif/:offerId/recapitulatif">
          <LogRouteNavigation
            route={{ title: 'Offre collective - duplication - récapitulatif' }}
          >
            {collectiveOffer ? (
              <CollectiveOfferSummaryCreation
                offer={collectiveOffer}
                // @ts-ignore this file will be deleted when we will remove the duplication pages code
                setOffer={setCollectiveOffer}
              />
            ) : (
              <Spinner />
            )}
          </LogRouteNavigation>
        </Route>
      </CollectiveOfferLayout>
    </Switch>
  )
}

export default CollectiveOfferCreationRoutes
