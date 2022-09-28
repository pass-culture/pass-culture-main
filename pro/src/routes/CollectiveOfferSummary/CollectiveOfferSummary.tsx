import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import {
  getEducationalCategoriesAdapter,
  EducationalCategories,
  CollectiveOffer,
} from 'core/OfferEducational'
import getCollectiveOfferAdapter from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import CollectiveOfferLayout from 'new_components/CollectiveOfferLayout'
import CollectiveOfferSummaryScreen from 'screens/CollectiveOfferSummary'

const CollectiveOfferSummary = () => {
  const { offerId } = useParams<{ offerId: string }>()
  const notify = useNotification()

  const [offer, setOffer] = useState<CollectiveOffer | null>(null)
  const [categories, setCategories] = useState<EducationalCategories | null>(
    null
  )

  const reloadCollectiveOffer = () => {
    getCollectiveOfferAdapter(offerId).then(response =>
      setOffer(response.payload)
    )
  }

  useEffect(() => {
    const loadData = async () => {
      const [offerResponse, categoriesResponse] = await Promise.all([
        getCollectiveOfferAdapter(offerId),
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
      <CollectiveOfferSummaryScreen
        offer={offer}
        categories={categories}
        reloadCollectiveOffer={reloadCollectiveOffer}
      />
    </CollectiveOfferLayout>
  )
}

export default CollectiveOfferSummary
