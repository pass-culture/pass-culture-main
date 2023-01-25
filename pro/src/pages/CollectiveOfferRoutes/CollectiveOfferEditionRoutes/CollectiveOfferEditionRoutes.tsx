/* istanbul ignore file: DEBT, TO FIX*/
import React, { useCallback, useEffect, useState } from 'react'
import { Route, Switch, useLocation } from 'react-router-dom'

import CollectiveOfferLayout from 'components/CollectiveOfferLayout'
import PageTitle from 'components/PageTitle/PageTitle'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  isCollectiveOffer,
} from 'core/OfferEducational'
import getCollectiveOfferAdapter from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import getCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import CollectiveOfferEdition from 'pages/CollectiveOfferEdition'
import CollectiveOfferStockEdition from 'pages/CollectiveOfferStockEdition'
import CollectiveOfferSummaryEdition from 'pages/CollectiveOfferSummaryEdition'
import CollectiveOfferVisibility from 'pages/CollectiveOfferVisibility/CollectiveOfferEditionVisibility'
import Spinner from 'ui-kit/Spinner/Spinner'

import { getActiveStep } from '../utils/getActiveStep'

interface CollectiveOfferEditionRoutesProps {
  offerId: string
  isTemplate: boolean
}

const CollectiveOfferEditionRoutes = ({
  offerId,
  isTemplate,
}: CollectiveOfferEditionRoutesProps): JSX.Element => {
  const location = useLocation()

  const [offer, setOffer] = useState<
    CollectiveOffer | CollectiveOfferTemplate
  >()

  const loadCollectiveOffer = useCallback(async () => {
    const adapter = isTemplate
      ? getCollectiveOfferTemplateAdapter
      : getCollectiveOfferAdapter
    const response = await adapter(offerId)
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
      isTemplate={isTemplate}
      title={isSummaryPage ? 'Récapitulatif' : 'Éditer une offre collective'}
      subTitle={offer.name}
      breadCrumpProps={
        isSummaryPage
          ? undefined
          : {
              activeStep: getActiveStep(location.pathname),
              offerId: computeURLCollectiveOfferId(offerId, isTemplate),
              isCreatingOffer: false,
            }
      }
    >
      <Switch>
        <Route path="/offre/:offerId/collectif/edition">
          <PageTitle title="Détails de l'offre" />
          <CollectiveOfferEdition
            offer={offer}
            setOffer={setOffer}
            reloadCollectiveOffer={loadCollectiveOffer}
          />
        </Route>
        <Route path="/offre/:offerId/collectif/recapitulatif">
          <PageTitle title="Récapitulatif" />
          <CollectiveOfferSummaryEdition
            offer={offer}
            reloadCollectiveOffer={loadCollectiveOffer}
          />
        </Route>
        {!isTemplate && isCollectiveOffer(offer) && (
          <>
            <Route path="/offre/:offerId/collectif/stocks/edition">
              <PageTitle title="Date et prix" />
              <CollectiveOfferStockEdition
                offer={offer}
                reloadCollectiveOffer={loadCollectiveOffer}
              />
            </Route>
            <Route path="/offre/:offerId/collectif/visibilite/edition">
              <PageTitle title="Visibilité" />
              <CollectiveOfferVisibility
                offer={offer}
                reloadCollectiveOffer={loadCollectiveOffer}
              />
            </Route>
          </>
        )}
      </Switch>
    </CollectiveOfferLayout>
  )
}

export default CollectiveOfferEditionRoutes
