import React, { useEffect, useState } from 'react'
import { Route, Switch, useLocation } from 'react-router-dom'

import { LogRouteNavigation } from 'app/AppRouter/LogRouteNavigation'
import CollectiveOfferLayout from 'components/CollectiveOfferLayout'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  isCollectiveOffer,
} from 'core/OfferEducational'
import getCollectiveOfferAdapter from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import getCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'
import useActiveFeature from 'hooks/useActiveFeature'
import CollectiveOfferConfirmation from 'pages/CollectiveOfferConfirmation'
import CollectiveOfferCreation from 'pages/CollectiveOfferCreation'
import CollectiveOfferStockCreation from 'pages/CollectiveOfferStockCreation'
import CollectiveOfferSummaryCreation from 'pages/CollectiveOfferSummaryCreation'
import CollectiveOfferVisibilityCreation from 'pages/CollectiveOfferVisibility/CollectiveOfferCreationVisibility'
import Spinner from 'ui-kit/Spinner/Spinner'

import { getActiveStep } from '../utils/getActiveStep'

interface CollectiveOfferCreationRoutesProps {
  offerId?: string
  isTemplate: boolean
}

const CollectiveOfferCreationRoutes = ({
  offerId,
  isTemplate,
}: CollectiveOfferCreationRoutesProps): JSX.Element => {
  const location = useLocation()
  const shouldRenderTemplateOffer =
    isTemplate || location.pathname.includes('vitrine')

  const [offer, setOffer] = useState<
    CollectiveOffer | CollectiveOfferTemplate
  >()

  const isSubtypeChosenAtCreation = useActiveFeature(
    'WIP_CHOOSE_COLLECTIVE_OFFER_TYPE_AT_CREATION'
  )

  useEffect(() => {
    if (!offerId) {
      return
    }

    const loadCollectiveOffer = async (offerId: string) => {
      const adapter = shouldRenderTemplateOffer
        ? getCollectiveOfferTemplateAdapter
        : getCollectiveOfferAdapter

      const response = await adapter(offerId)
      if (response.isOk) {
        setOffer(response.payload)
      }
    }

    loadCollectiveOffer(offerId)
  }, [offerId])

  const activeStep = getActiveStep(location.pathname)

  return (
    <Switch>
      <Route path={'/offre/:offerId/collectif/confirmation'}>
        <LogRouteNavigation
          route={{ title: 'Offre collective - confirmation' }}
        >
          {offer ? <CollectiveOfferConfirmation offer={offer} /> : <Spinner />}
        </LogRouteNavigation>
      </Route>
      <Route path={'/offre/:offerId/collectif/vitrine/confirmation'}>
        <LogRouteNavigation
          route={{ title: 'Offre vitrine collective - confirmation' }}
        >
          {offer ? <CollectiveOfferConfirmation offer={offer} /> : <Spinner />}
        </LogRouteNavigation>
      </Route>

      <Route
        path={[
          '/offre/:offerId/collectif',
          '/offre/creation/collectif',
          '/offre/collectif/:offerId/creation',
          '/offre/creation/collectif/vitrine',
          '/offre/collectif/vitrine/:offerId/creation',
        ]}
        exact={false}
      >
        <CollectiveOfferLayout
          title={
            isCollectiveOffer(offer) && offer?.templateId
              ? 'Créer une offre pour un établissement scolaire'
              : 'Créer une nouvelle offre collective'
          }
          subTitle={offer?.name}
          breadCrumpProps={{
            activeStep: activeStep,
            isCreatingOffer: true,
            offerId,
          }}
          isTemplate={shouldRenderTemplateOffer}
        >
          <Switch>
            <Route path="/offre/creation/collectif/vitrine">
              <LogRouteNavigation
                route={{ title: 'Offre vitrine collective - création' }}
              >
                <CollectiveOfferCreation
                  offer={offer}
                  setOffer={setOffer}
                  isTemplate
                />
              </LogRouteNavigation>
            </Route>
            <Route path="/offre/creation/collectif">
              <LogRouteNavigation
                route={{ title: 'Offre collective - création' }}
              >
                <CollectiveOfferCreation offer={offer} setOffer={setOffer} />
              </LogRouteNavigation>
            </Route>
            {isSubtypeChosenAtCreation && (
              <Route path="/offre/collectif/:offerId/creation">
                <LogRouteNavigation
                  route={{ title: 'Offre collective - création' }}
                >
                  {offer ? (
                    <CollectiveOfferCreation
                      offer={offer}
                      setOffer={setOffer}
                    />
                  ) : (
                    <Spinner />
                  )}
                </LogRouteNavigation>
              </Route>
            )}
            {isSubtypeChosenAtCreation && (
              <Route path="/offre/collectif/vitrine/:offerId/creation">
                <LogRouteNavigation
                  route={{ title: 'Offre vitrine collective - création' }}
                >
                  {offer ? (
                    <CollectiveOfferCreation
                      offer={offer}
                      setOffer={setOffer}
                      isTemplate
                    />
                  ) : (
                    <Spinner />
                  )}
                </LogRouteNavigation>
              </Route>
            )}
            <Route path="/offre/:offerId/collectif/stocks">
              <LogRouteNavigation
                route={{ title: 'Offre collective - création de stocks' }}
              >
                {offer && isCollectiveOffer(offer) ? (
                  <CollectiveOfferStockCreation
                    offer={offer}
                    setOffer={setOffer}
                  />
                ) : (
                  <Spinner />
                )}
              </LogRouteNavigation>
            </Route>
            <Route path="/offre/:offerId/collectif/visibilite">
              <LogRouteNavigation
                route={{ title: 'Offre collective - visibilité' }}
              >
                {offer && isCollectiveOffer(offer) ? (
                  <CollectiveOfferVisibilityCreation
                    offer={offer}
                    setOffer={setOffer}
                  />
                ) : (
                  <Spinner />
                )}
              </LogRouteNavigation>
            </Route>
            <Route path={'/offre/:offerId/collectif/creation/recapitulatif'}>
              <LogRouteNavigation
                route={{
                  title:
                    'Offre collective - récapitulation de création d’offre',
                }}
              >
                {offer ? (
                  <CollectiveOfferSummaryCreation
                    offer={offer}
                    setOffer={setOffer}
                  />
                ) : (
                  <Spinner />
                )}
              </LogRouteNavigation>
            </Route>
            <Route
              path={'/offre/:offerId/collectif/vitrine/creation/recapitulatif'}
            >
              <LogRouteNavigation
                route={{
                  title:
                    'Offre vitrine collective - récapitulation de création d’offre',
                }}
              >
                {offer ? (
                  <CollectiveOfferSummaryCreation
                    offer={offer}
                    setOffer={setOffer}
                  />
                ) : (
                  <Spinner />
                )}
              </LogRouteNavigation>
            </Route>
          </Switch>
        </CollectiveOfferLayout>
      </Route>
    </Switch>
  )
}

export default CollectiveOfferCreationRoutes
