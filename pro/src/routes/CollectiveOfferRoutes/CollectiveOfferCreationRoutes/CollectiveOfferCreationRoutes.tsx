import React, { useEffect, useState } from 'react'
import { Route, Switch } from 'react-router-dom'

import { CollectiveOffer, CollectiveOfferTemplate } from 'core/OfferEducational'
import getCollectiveOfferAdapter from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import getCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'
import CollectiveOfferLayout from 'new_components/CollectiveOfferLayout'
import CollectiveOfferTemplateCreation from 'pages/CollectiveOfferTemplateCreation'
import CollectiveOfferConfirmation from 'routes/CollectiveOfferConfirmation'
import CollectiveOfferStockCreation from 'routes/CollectiveOfferStockCreation'
import CollectiveOfferSummaryCreation from 'routes/CollectiveOfferSummaryCreation'
import CollectiveOfferVisibilityCreation from 'routes/CollectiveOfferVisibility/CollectiveOfferCreationVisibility'
import OfferEducationalCreation from 'routes/OfferEducationalCreation'
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
          '/offre/creation/collectif/vitrine',
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
              <OfferEducationalCreation />
            </Route>
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
