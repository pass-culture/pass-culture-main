/* istanbul ignore file: DEBT, TO FIX*/
import React, { useCallback, useEffect, useState } from 'react'
import { Routes, Route } from 'react-router-dom-v5-compat'

import CollectiveOfferLayout from 'components/CollectiveOfferLayout'
import PageTitle from 'components/PageTitle/PageTitle'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  isCollectiveOffer,
} from 'core/OfferEducational'
import getCollectiveOfferAdapter from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import getCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'
import CollectiveOfferVisibility from 'pages/CollectiveOfferVisibility/CollectiveOfferEditionVisibility'
import Spinner from 'ui-kit/Spinner/Spinner'

interface CollectiveOfferEditionRoutesProps {
  offerId: string
  isTemplate: boolean
}

const CollectiveOfferEditionRoutes = ({
  offerId,
  isTemplate,
}: CollectiveOfferEditionRoutesProps): JSX.Element => {
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

  return (
    <CollectiveOfferLayout subTitle={offer.name}>
      <Routes>
        {!isTemplate && isCollectiveOffer(offer) && (
          <>
            <Route
              path="/offre/:offerId/collectif/visibilite/edition"
              element={
                <>
                  <PageTitle title="Visibilité" />
                  <CollectiveOfferVisibility
                    offer={offer}
                    reloadCollectiveOffer={loadCollectiveOffer}
                  />
                </>
              }
            />
          </>
        )}
      </Routes>
    </CollectiveOfferLayout>
  )
}

export default CollectiveOfferEditionRoutes
