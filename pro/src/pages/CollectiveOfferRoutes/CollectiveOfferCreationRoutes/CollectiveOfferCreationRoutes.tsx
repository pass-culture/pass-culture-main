/* istanbul ignore file: DEBT, TO FIX*/
import React, { useEffect, useState } from 'react'
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
      <Route
        path={[
          '/offre/:offerId/collectif/confirmation',
          '/offre/:offerId/collectif/vitrine/confirmation',
        ]}
      >
        <PageTitle title="Confirmation" />
        {offer ? <CollectiveOfferConfirmation offer={offer} /> : <Spinner />}
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
        <PageTitle title="Détails de l'offre" />
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
              <CollectiveOfferCreation
                offer={offer}
                setOffer={setOffer}
                isTemplate
              />
            </Route>
            <Route path="/offre/creation/collectif">
              <CollectiveOfferCreation offer={offer} setOffer={setOffer} />
            </Route>
            <Route path="/offre/collectif/:offerId/creation">
              {offer ? (
                <CollectiveOfferCreation offer={offer} setOffer={setOffer} />
              ) : (
                <Spinner />
              )}
            </Route>
            <Route path="/offre/collectif/vitrine/:offerId/creation">
              {offer ? (
                <CollectiveOfferCreation
                  offer={offer}
                  setOffer={setOffer}
                  isTemplate
                />
              ) : (
                <Spinner />
              )}
            </Route>
            <Route path="/offre/:offerId/collectif/stocks">
              <PageTitle title="Vos stocks" />
              {offer && isCollectiveOffer(offer) ? (
                <CollectiveOfferStockCreation
                  offer={offer}
                  setOffer={setOffer}
                />
              ) : (
                <Spinner />
              )}
            </Route>
            <Route path="/offre/:offerId/collectif/visibilite">
              <PageTitle title="Visibilité" />
              {offer && isCollectiveOffer(offer) ? (
                <CollectiveOfferVisibilityCreation
                  offer={offer}
                  setOffer={setOffer}
                />
              ) : (
                <Spinner />
              )}
            </Route>
            <Route
              path={[
                '/offre/:offerId/collectif/creation/recapitulatif',
                '/offre/:offerId/collectif/vitrine/creation/recapitulatif',
              ]}
            >
              <PageTitle title="Récapitulatif" />
              {offer ? (
                <CollectiveOfferSummaryCreation
                  offer={offer}
                  setOffer={setOffer}
                />
              ) : (
                <Spinner />
              )}
            </Route>
          </Switch>
        </CollectiveOfferLayout>
      </Route>
    </Switch>
  )
}

export default CollectiveOfferCreationRoutes
