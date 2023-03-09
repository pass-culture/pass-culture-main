import React from 'react'
import { useParams, Route, Switch } from 'react-router-dom'

import { extractOfferIdAndOfferTypeFromRouteParams } from 'core/OfferEducational'

import CollectiveOfferCreationRoutes from './CollectiveOfferCreationRoutes'
import CollectiveOfferEditionRoutes from './CollectiveOfferEditionRoutes'

const CollectiveOfferRoutes = (): JSX.Element => {
  const { offerId: offerIdFromParams } = useParams<{
    offerId: string
  }>()

  const { offerId, isTemplate } =
    extractOfferIdAndOfferTypeFromRouteParams(offerIdFromParams)

  return (
    <Switch>
      <Route
        path={[
          '/offre/:offerId/collectif/stocks/edition',
          '/offre/:offerId/collectif/visibilite/edition',
          '/offre/:offerId/collectif/recapitulatif',
        ]}
      >
        <CollectiveOfferEditionRoutes
          offerId={offerId}
          isTemplate={isTemplate}
        />
      </Route>
      <Route path={['/offre/creation/collectif']}>
        <CollectiveOfferCreationRoutes
          offerId={undefined}
          isTemplate={isTemplate}
        />
      </Route>
      <Route
        path={[
          '/offre/collectif/:offerId/creation',
          '/offre/collectif/vitrine/:offerId/creation',
          '/offre/:offerId/collectif/stocks',
          '/offre/:offerId/collectif/visibilite',
          '/offre/:offerId/collectif/confirmation',
          '/offre/:offerId/collectif/vitrine/confirmation',
          '/offre/:offerId/collectif/creation/recapitulatif',
          '/offre/:offerId/collectif/vitrine/creation/recapitulatif',
        ]}
      >
        <CollectiveOfferCreationRoutes
          offerId={offerId}
          isTemplate={isTemplate}
        />
      </Route>
    </Switch>
  )
}

export default CollectiveOfferRoutes
