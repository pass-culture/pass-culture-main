import React, { useEffect, useState } from 'react'
import { Route, Switch } from 'react-router-dom'

import Spinner from 'components/layout/Spinner'
import { CollectiveOffer, CollectiveOfferTemplate } from 'core/OfferEducational'
import getCollectiveOfferAdapter from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import getCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'
import CollectiveOfferLayout from 'new_components/CollectiveOfferLayout'
import CollectiveOfferConfirmation from 'routes/CollectiveOfferConfirmation'
import CollectiveOfferVisibilityCreation from 'routes/CollectiveOfferVisibility/CollectiveOfferCreationVisibility'
import OfferEducationalCreation from 'routes/OfferEducationalCreation'
import OfferEducationalStockCreation from 'routes/OfferEducationalStockCreation'

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

  return (
    <Switch>
      <Route path="/offre/:offerId/collectif/confirmation">
        {offer ? <CollectiveOfferConfirmation offer={offer} /> : <Spinner />}
      </Route>
      <Route
        path={['/offre/:offerId/collectif', '/offre/creation/collectif']}
        exact={false}
      >
        <CollectiveOfferLayout
          title="Créer une nouvelle offre collective"
          subTitle={collectiveOffer?.name}
          breadCrumpProps={{
            activeStep: getActiveStep(location.pathname),
            isCreatingOffer: true,
          }}
        >
          <Switch>
            <Route path="/offre/creation/collectif">
              <OfferEducationalCreation />
            </Route>
            <Route path="/offre/:offerId/collectif/stocks">
              {collectiveOffer ? (
                <OfferEducationalStockCreation offer={collectiveOffer} />
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
          </Switch>
        </CollectiveOfferLayout>
      </Route>
    </Switch>
  )
}

export default CollectiveOfferCreationRoutes
