import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router'

import { GetCollectiveOfferTemplateResponseModel } from 'apiClient/v1'
import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import { extractOfferIdAndOfferTypeFromRouteParams } from 'core/OfferEducational'
import getCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'
import CollectiveOfferLayout from 'new_components/CollectiveOfferLayout'
import CollectiveOfferSummary from 'screens/CollectiveOfferSummary'

const CollectiveOfferTemplateSummary = () => {
  const { offerId: offerIdFromParams } = useParams<{ offerId: string }>()
  const notify = useNotification()

  const { offerId } =
    extractOfferIdAndOfferTypeFromRouteParams(offerIdFromParams)

  const [offer, setOffer] =
    useState<GetCollectiveOfferTemplateResponseModel | null>(null)

  useEffect(() => {
    const loadOffer = async () => {
      const response = await getCollectiveOfferTemplateAdapter(offerId)

      if (!response.isOk) {
        return notify.error(response.message)
      }

      setOffer(response.payload)
    }

    loadOffer()
  }, [offerId])

  return offer === null ? (
    <Spinner />
  ) : (
    <CollectiveOfferLayout title="Récapitulatif" subTitle={offer.name}>
      <CollectiveOfferSummary offer={offer} />
    </CollectiveOfferLayout>
  )
}

export default CollectiveOfferTemplateSummary
