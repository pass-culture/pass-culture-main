import React from 'react'
import { useParams, Route, Switch } from 'react-router-dom'

import { extractOfferIdAndOfferTypeFromRouteParams } from 'core/OfferEducational'
import useActiveFeature from 'hooks/useActiveFeature'

import CollectiveOfferCreationFromTemplateRoutes from './CollectiveOfferCreationFromTemplateRoutes/CollectiveOfferCreationFromTemplateRoutes'
import CollectiveOfferCreationRoutes from './CollectiveOfferCreationRoutes'
import CollectiveOfferEditionRoutes from './CollectiveOfferEditionRoutes'
import CollectiveOfferTemplateEditionRoutes from './CollectiveOfferTemplateEditionRoutes'

const CollectiveOfferRoutes = (): JSX.Element => {
  const isCollectiveOfferDuplicationActive = useActiveFeature(
    'WIP_CREATE_COLLECTIVE_OFFER_FROM_TEMPLATE'
  )

  const { offerId: offerIdFromParams } = useParams<{
    offerId: string
  }>()

  const { offerId, isShowcase } =
    extractOfferIdAndOfferTypeFromRouteParams(offerIdFromParams)

  const formattedOfferId = offerId !== 'creation' ? offerId : undefined

  return (
    <Switch>
      {isCollectiveOfferDuplicationActive && (
        <Route
          path={[
            '/offre/duplication/collectif/:offerId/stocks',
            '/offre/duplication/collectif/:offerId/visibilite',
            '/offre/duplication/collectif/:offerId/confirmation',
            '/offre/duplication/:templateId',
          ]}
        >
          <CollectiveOfferCreationFromTemplateRoutes />
        </Route>
      )}
      <Route
        path={[
          '/offre/:offerId/collectif/edition',
          '/offre/:offerId/collectif/stocks/edition',
          '/offre/:offerId/collectif/visibilite/edition',
          '/offre/:offerId/collectif/recapitulatif',
        ]}
      >
        {isShowcase ? (
          <CollectiveOfferTemplateEditionRoutes offerId={offerId} />
        ) : (
          <CollectiveOfferEditionRoutes offerId={offerId} />
        )}
      </Route>
      <Route
        path={[
          '/offre/creation/collectif',
          '/offre/creation/collectif/vitrine',
          '/offre/:offerId/collectif/stocks',
          '/offre/:offerId/collectif/visibilite',
          '/offre/:offerId/collectif/confirmation',
          '/offre/:offerId/collectif/creation/recapitulatif',
        ]}
      >
        <CollectiveOfferCreationRoutes
          offerId={formattedOfferId}
          isTemplate={isShowcase}
        />
      </Route>
    </Switch>
  )
}

export default CollectiveOfferRoutes
