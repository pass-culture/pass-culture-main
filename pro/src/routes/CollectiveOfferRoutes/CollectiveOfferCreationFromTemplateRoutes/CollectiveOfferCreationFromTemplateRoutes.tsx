import React, { useEffect, useState } from 'react'
import { Route, Switch, useParams } from 'react-router-dom'

import Spinner from 'components/layout/Spinner'
import { CollectiveOffer } from 'core/OfferEducational'
import getCollectiveOfferAdapter from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import CollectiveOfferLayout from 'new_components/CollectiveOfferLayout'
import CollectiveOfferConfirmation from 'routes/CollectiveOfferConfirmation'
import CollectiveOfferCreationFromTemplate from 'routes/CollectiveOfferCreationFromTemplate'
import CollectiveOfferStockCreationFromTemplate from 'routes/CollectiveOfferStockCreationFromTemplate'
import CollectiveOfferSummaryCreation from 'routes/CollectiveOfferSummaryCreation'
import CollectiveOfferCreationVisibility from 'routes/CollectiveOfferVisibility/CollectiveOfferCreationVisibility'

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
        {collectiveOffer ? (
          <CollectiveOfferConfirmation offer={collectiveOffer} />
        ) : (
          <Spinner />
        )}
      </Route>
      <CollectiveOfferLayout
        title="Créer une offre pour un établissement scolaire"
        subTitle={collectiveOffer?.name}
        breadCrumpProps={{
          activeStep: getActiveStep(location.pathname),
          isCreatingOffer: true,
        }}
      >
        <Route path="/offre/duplication/collectif/:templateId" exact>
          <CollectiveOfferCreationFromTemplate />
        </Route>
        <Route path="/offre/duplication/collectif/:offerId/stocks">
          {collectiveOffer ? (
            <CollectiveOfferStockCreationFromTemplate offer={collectiveOffer} />
          ) : (
            <Spinner />
          )}
        </Route>
        <Route path="/offre/duplication/collectif/:offerId/visibilite">
          {collectiveOffer ? (
            <CollectiveOfferCreationVisibility
              setOffer={setCollectiveOffer}
              isDuplicatingOffer
            />
          ) : (
            <Spinner />
          )}
        </Route>
        <Route path="/offre/duplication/collectif/:offerId/recapitulatif">
          {collectiveOffer ? (
            <CollectiveOfferSummaryCreation offer={collectiveOffer} />
          ) : (
            <Spinner />
          )}
        </Route>
      </CollectiveOfferLayout>
    </Switch>
  )
}

export default CollectiveOfferCreationRoutes
