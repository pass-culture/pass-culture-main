import React, { useCallback, useEffect, useState } from 'react'
import { Route, Switch, useLocation, useParams } from 'react-router-dom'

import Spinner from 'components/layout/Spinner'
import {
  CollectiveOfferTemplate,
  extractOfferIdAndOfferTypeFromRouteParams,
} from 'core/OfferEducational'
import getCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'
import CollectiveOfferLayout from 'new_components/CollectiveOfferLayout'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import CollectiveOfferEdition from 'routes/CollectiveOfferEdition'
import CollectiveOfferTemplateStockEdition from 'routes/CollectiveOfferTemplateStockEdition'
import CollectiveOfferTemplateSummary from 'routes/CollectiveOfferTemplateSummary'

/* istanbul ignore next: DEBT, TO FIX */
const CollectiveOfferTemplateEditionRoutes = (): JSX.Element => {
  const { offerId: offerIdFromParams } = useParams<{ offerId: string }>()
  const { offerId } =
    extractOfferIdAndOfferTypeFromRouteParams(offerIdFromParams)
  const location = useLocation()
  const [offer, setOffer] = useState<CollectiveOfferTemplate>()

  const loadCollectiveOfferTemplate = useCallback(async () => {
    const response = await getCollectiveOfferTemplateAdapter(offerId)
    if (response.isOk) {
      setOffer(response.payload)
    }
  }, [offerId])

  useEffect(() => {
    loadCollectiveOfferTemplate()
  }, [])

  if (!offer) {
    return <Spinner />
  }

  const getActiveStep = (pathname: string) => {
    if (pathname.includes('stocks')) {
      return OfferBreadcrumbStep.STOCKS
    }

    return OfferBreadcrumbStep.DETAILS
  }

  const isSummaryPage = location.pathname.includes('recapitulatif')

  return (
    <CollectiveOfferLayout
      isTemplate
      title={isSummaryPage ? 'Récapitulatif' : 'Éditer une offre collective'}
      subTitle={offer.name}
      breadCrumpProps={
        isSummaryPage
          ? undefined
          : {
              activeStep: getActiveStep(location.pathname),
              offerId: `T-${offer.id}`,
              isCreatingOffer: false,
            }
      }
    >
      <Switch>
        <Route path="/offre/:offerId(T-[A-Z0-9]+)/collectif/edition" exact>
          <CollectiveOfferEdition
            offer={offer}
            reloadCollectiveOffer={loadCollectiveOfferTemplate}
          />
        </Route>
        <Route path="/offre/:offerId(T-[A-Z0-9]+)/collectif/stocks/edition">
          <CollectiveOfferTemplateStockEdition
            offer={offer}
            reloadCollectiveOffer={loadCollectiveOfferTemplate}
          />
        </Route>
        <Route path="/offre/:offerId(T-[A-Z0-9]+)/collectif/recapitulatif">
          <CollectiveOfferTemplateSummary offer={offer} />
        </Route>
      </Switch>
    </CollectiveOfferLayout>
  )
}

export default CollectiveOfferTemplateEditionRoutes
