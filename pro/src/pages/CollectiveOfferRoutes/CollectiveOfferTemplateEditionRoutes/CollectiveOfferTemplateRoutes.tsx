import React, { useCallback, useEffect, useState } from 'react'
import { Route, Switch, useLocation } from 'react-router-dom'

import CollectiveOfferLayout from 'components/CollectiveOfferLayout'
import { CollectiveOfferTemplate } from 'core/OfferEducational'
import getCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import CollectiveOfferEdition from 'pages/CollectiveOfferEdition'
import CollectiveOfferTemplateStockEdition from 'pages/CollectiveOfferTemplateStockEdition'
import CollectiveOfferTemplateSummaryEdition from 'pages/CollectiveOfferTemplateSummaryEdition'
import Spinner from 'ui-kit/Spinner/Spinner'

import { getActiveStep } from '../utils/getActiveStep'

interface CollectiveOfferTemplateRoutesProps {
  offerId: string
}

/* istanbul ignore next: DEBT, TO FIX */
const CollectiveOfferTemplateEditionRoutes = ({
  offerId,
}: CollectiveOfferTemplateRoutesProps): JSX.Element => {
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
              offerId: computeURLCollectiveOfferId(offerId, true),
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
          <CollectiveOfferTemplateSummaryEdition offer={offer} />
        </Route>
      </Switch>
    </CollectiveOfferLayout>
  )
}

export default CollectiveOfferTemplateEditionRoutes
