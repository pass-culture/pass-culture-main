import React, { useEffect, useState } from 'react'
import { Route, Switch, useLocation } from 'react-router-dom'

import CollectiveOfferLayout from 'components/CollectiveOfferLayout'
import { CollectiveOffer, CollectiveOfferTemplate } from 'core/OfferEducational'
import getCollectiveOfferAdapter from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import getCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'
import useActiveFeature from 'hooks/useActiveFeature'
import CollectiveOfferConfirmation from 'pages/CollectiveOfferConfirmation'
import CollectiveOfferCreation from 'pages/CollectiveOfferCreation'
import CollectiveOfferStockCreation from 'pages/CollectiveOfferStockCreation'
import CollectiveOfferSummaryCreation from 'pages/CollectiveOfferSummaryCreation'
import CollectiveOfferTemplateCreation from 'pages/CollectiveOfferTemplateCreation'
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

  const [collectiveOffer, setCollectiveOffer] = useState<CollectiveOffer>()
  const [collectiveOfferTemplate, setCollectiveOfferTemplate] =
    useState<CollectiveOfferTemplate>()

  const isSubtypeChosenAtCreation = useActiveFeature(
    'WIP_CHOOSE_COLLECTIVE_OFFER_TYPE_AT_CREATION'
  )

  useEffect(() => {
    if (!offerId) return

    const loadCollectiveOffer = async (offerId: string) => {
      const response = await getCollectiveOfferAdapter(offerId)
      if (response.isOk) {
        setCollectiveOffer(response.payload)
      }
    }

    const loadCollectiveOfferTemplate = async (offerId: string) => {
      const response = await getCollectiveOfferTemplateAdapter(offerId)
      if (response.isOk) {
        setCollectiveOfferTemplate(response.payload)
      }
    }

    if (shouldRenderTemplateOffer) {
      loadCollectiveOfferTemplate(offerId)
    } else {
      loadCollectiveOffer(offerId)
    }
  }, [offerId])

  const offer = shouldRenderTemplateOffer
    ? collectiveOfferTemplate
    : collectiveOffer
  const activeStep = getActiveStep(location.pathname)

  return (
    <Switch>
      <Route
        path={[
          '/offre/:offerId/collectif/confirmation',
          '/offre/:offerId/collectif/vitrine/confirmation',
        ]}
      >
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
        <CollectiveOfferLayout
          title={
            collectiveOffer?.templateId
              ? 'Créer une offre pour un établissement scolaire'
              : 'Créer une nouvelle offre collective'
          }
          subTitle={collectiveOffer?.name}
          breadCrumpProps={{
            activeStep: activeStep,
            isCreatingOffer: true,
            offerId,
          }}
          isTemplate={shouldRenderTemplateOffer}
        >
          <Switch>
            <Route path="/offre/creation/collectif/vitrine">
              <CollectiveOfferTemplateCreation
                offer={collectiveOfferTemplate}
                setOfferTemplate={setCollectiveOfferTemplate}
              />
            </Route>
            <Route path="/offre/creation/collectif">
              <CollectiveOfferCreation
                offer={collectiveOffer}
                setOffer={setCollectiveOffer}
              />
            </Route>
            {isSubtypeChosenAtCreation && (
              <Route path="/offre/collectif/:offerId/creation">
                {collectiveOffer ? (
                  <CollectiveOfferCreation
                    offer={collectiveOffer}
                    setOffer={setCollectiveOffer}
                  />
                ) : (
                  <Spinner />
                )}
              </Route>
            )}
            {isSubtypeChosenAtCreation && (
              <Route path="/offre/collectif/vitrine/:offerId/creation">
                {collectiveOfferTemplate ? (
                  <CollectiveOfferTemplateCreation
                    offer={collectiveOfferTemplate}
                    setOfferTemplate={setCollectiveOfferTemplate}
                  />
                ) : (
                  <Spinner />
                )}
              </Route>
            )}
            <Route path="/offre/:offerId/collectif/stocks">
              {collectiveOffer ? (
                <CollectiveOfferStockCreation
                  offer={collectiveOffer}
                  setOffer={setCollectiveOffer}
                />
              ) : (
                <Spinner />
              )}
            </Route>
            <Route path="/offre/:offerId/collectif/visibilite">
              {collectiveOffer ? (
                <CollectiveOfferVisibilityCreation
                  offer={collectiveOffer}
                  setOffer={setCollectiveOffer}
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
              {offer ? (
                <CollectiveOfferSummaryCreation
                  offer={offer}
                  setOffer={
                    offer.isTemplate
                      ? setCollectiveOfferTemplate
                      : setCollectiveOffer
                  }
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
