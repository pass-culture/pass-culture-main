import React, { useCallback, useEffect, useState } from 'react'
import { Route, Switch, useLocation } from 'react-router-dom'

import { LogRouteNavigation } from 'app/AppRouter/LogRouteNavigation'
import CollectiveOfferLayout from 'components/CollectiveOfferLayout'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  isCollectiveOffer,
  isCollectiveOfferTemplate,
} from 'core/OfferEducational'
import getCollectiveOfferAdapter from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import getCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import CollectiveOfferEdition from 'pages/CollectiveOfferEdition'
import CollectiveOfferStockEdition from 'pages/CollectiveOfferStockEdition'
import CollectiveOfferSummaryEdition from 'pages/CollectiveOfferSummaryEdition'
import CollectiveOfferTemplateStockEdition from 'pages/CollectiveOfferTemplateStockEdition'
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
          <LogRouteNavigation route={{ title: 'Offre collective - edition' }}>
            <CollectiveOfferEdition
              offer={offer}
              reloadCollectiveOffer={loadCollectiveOffer}
            />
          </LogRouteNavigation>
        </Route>
        <Route path="/offre/:offerId/collectif/recapitulatif">
          <LogRouteNavigation
            route={{ title: 'Offre collective - récapitulatif' }}
          >
            <CollectiveOfferSummaryEdition
              offer={offer}
              reloadCollectiveOffer={loadCollectiveOffer}
            />
          </LogRouteNavigation>
        </Route>

        {!isTemplate && isCollectiveOffer(offer) && (
          <>
            <Route path="/offre/:offerId/collectif/stocks/edition">
              <LogRouteNavigation
                route={{ title: 'Offre collective - edition de stocks' }}
              >
                <CollectiveOfferStockEdition
                  offer={offer}
                  reloadCollectiveOffer={loadCollectiveOffer}
                />
              </LogRouteNavigation>
            </Route>
            <Route path="/offre/:offerId/collectif/visibilite/edition">
              <LogRouteNavigation
                route={{ title: 'Offre collective - édition de la visibilité' }}
              >
                <CollectiveOfferVisibility
                  offer={offer}
                  reloadCollectiveOffer={loadCollectiveOffer}
                />
              </LogRouteNavigation>
            </Route>
          </>
        )}
        {/* TODO delete this page when WIP_CHOOSE_COLLECTIVE_OFFER_TYPE_AT_CREATION feature is in prod */}
        {isTemplate && isCollectiveOfferTemplate(offer) && (
          <Route path="/offre/:offerId/collectif/stocks/edition">
            <LogRouteNavigation
              route={{ title: 'Offre collective - edition de stocks' }}
            >
              <CollectiveOfferTemplateStockEdition
                offer={offer}
                reloadCollectiveOffer={loadCollectiveOffer}
              />
            </LogRouteNavigation>
          </Route>
        )}
      </Switch>
    </CollectiveOfferLayout>
  )
}

export default CollectiveOfferEditionRoutes
