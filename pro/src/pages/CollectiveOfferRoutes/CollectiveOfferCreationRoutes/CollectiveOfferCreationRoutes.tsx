/* istanbul ignore file: DEBT, TO FIX*/
import React, { useEffect, useState } from 'react'
import { Routes, Route, useLocation } from 'react-router-dom-v5-compat'

import PageTitle from 'components/PageTitle/PageTitle'
import { CollectiveOffer, CollectiveOfferTemplate } from 'core/OfferEducational'
import getCollectiveOfferAdapter from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import getCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'
import CollectiveOfferCreation from 'pages/CollectiveOfferCreation'
import Spinner from 'ui-kit/Spinner/Spinner'

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

  return (
    <Routes>
      <Route
        path="/offre/creation/collectif/vitrine"
        element={
          <>
            <PageTitle title="Détails de l'offre" />
            <CollectiveOfferCreation
              offer={offer}
              setOffer={setOffer}
              isTemplate
            />
          </>
        }
      />
      <Route
        path="/offre/creation/collectif"
        element={
          <>
            <PageTitle title="Détails de l'offre" />{' '}
            <CollectiveOfferCreation offer={offer} setOffer={setOffer} />
          </>
        }
      />

      <Route
        path="/offre/collectif/:offerId/creation"
        element={
          <>
            <PageTitle title="Détails de l'offre" />
            {offer ? (
              <CollectiveOfferCreation offer={offer} setOffer={setOffer} />
            ) : (
              <Spinner />
            )}
          </>
        }
      />
      <Route
        path="/offre/collectif/vitrine/:offerId/creation"
        element={
          <>
            <PageTitle title="Détails de l'offre" />
            {offer ? (
              <CollectiveOfferCreation
                offer={offer}
                setOffer={setOffer}
                isTemplate
              />
            ) : (
              <Spinner />
            )}
          </>
        }
      />
    </Routes>
  )
}

export default CollectiveOfferCreationRoutes
