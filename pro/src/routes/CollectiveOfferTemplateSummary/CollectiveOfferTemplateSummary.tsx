import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import {
  extractOfferIdAndOfferTypeFromRouteParams,
  getEducationalCategoriesAdapter,
  EducationalCategories,
  CollectiveOfferTemplate,
} from 'core/OfferEducational'
import getCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import CollectiveOfferLayout from 'new_components/CollectiveOfferLayout'
import CollectiveOfferSummary from 'screens/CollectiveOfferSummary'

const CollectiveOfferTemplateSummary = () => {
  const { offerId: offerIdFromParams } = useParams<{ offerId: string }>()
  const notify = useNotification()

  const { offerId } =
    extractOfferIdAndOfferTypeFromRouteParams(offerIdFromParams)

  const [offer, setOffer] = useState<CollectiveOfferTemplate | null>(null)
  const [categories, setCategories] = useState<EducationalCategories | null>(
    null
  )

  useEffect(() => {
    const loadData = async () => {
      const [offerResponse, categoriesResponse] = await Promise.all([
        getCollectiveOfferTemplateAdapter(offerId),
        getEducationalCategoriesAdapter(),
      ])

      if (!offerResponse.isOk || !categoriesResponse.isOk) {
        return notify.error(GET_DATA_ERROR_MESSAGE)
      }

      setOffer(offerResponse.payload)
      setCategories(categoriesResponse.payload)
    }

    loadData()
  }, [offerId])

  const isReady = offer !== null && categories !== null

  return !isReady ? (
    <Spinner />
  ) : (
    <CollectiveOfferLayout title="Récapitulatif" subTitle={offer.name}>
      <CollectiveOfferSummary offer={offer} categories={categories} />
    </CollectiveOfferLayout>
  )
}

export default CollectiveOfferTemplateSummary
