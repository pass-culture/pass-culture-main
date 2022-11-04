import React, { useEffect, useState } from 'react'
import { Route, Switch } from 'react-router-dom'

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

    if (isTemplate) {
      loadCollectiveOfferTemplate(offerId)
    } else {
      loadCollectiveOffer(offerId)
    }
  }, [offerId])

  const offer = isTemplate ? collectiveOfferTemplate : collectiveOffer
  const activeStep = getActiveStep(location.pathname)

  return (
    <Switch>
      <Route path="/offre/:offerId/collectif/confirmation">
        {offer ? <CollectiveOfferConfirmation offer={offer} /> : <Spinner />}
      </Route>
      <Route
        path={[
          '/offre/:offerId/collectif',
          '/offre/creation/collectif',
          '/offre/collectif/:offerId/creation',
        ]}
        exact={false}
      >
        <CollectiveOfferLayout
          title="Créer une nouvelle offre collective"
          subTitle={collectiveOffer?.name}
          breadCrumpProps={{
            activeStep: activeStep,
            isCreatingOffer: true,
          }}
        >
          <Switch>
            <Route path="/offre/creation/collectif/vitrine">
              <CollectiveOfferTemplateCreation />
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
            <Route path="/offre/:offerId/collectif/stocks">
              {collectiveOffer ? (
                <CollectiveOfferStockCreation offer={collectiveOffer} />
              ) : (
                <Spinner />
              )}
            </Route>
            <Route path="/offre/:offerId/collectif/visibilite">
              {collectiveOffer ? (
                <CollectiveOfferVisibilityCreation
                  setOffer={setCollectiveOffer}
                />
              ) : (
                <Spinner />
              )}
            </Route>
            <Route path="/offre/:offerId/collectif/creation/recapitulatif">
              {offer ? (
                <CollectiveOfferSummaryCreation offer={offer} />
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
