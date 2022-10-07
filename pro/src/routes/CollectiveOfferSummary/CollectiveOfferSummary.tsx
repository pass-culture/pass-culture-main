import React, { useEffect, useState } from 'react'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import {
  getEducationalCategoriesAdapter,
  EducationalCategories,
  CollectiveOffer,
} from 'core/OfferEducational'
import CollectiveOfferSummaryScreen from 'screens/CollectiveOfferSummary'

interface CollectiveOfferSummaryProps {
  offer: CollectiveOffer
  reloadCollectiveOffer: () => void
}

const CollectiveOfferSummary = ({
  offer,
  reloadCollectiveOffer,
}: CollectiveOfferSummaryProps) => {
  const notify = useNotification()

  const [categories, setCategories] = useState<EducationalCategories | null>(
    null
  )

  useEffect(() => {
    const loadData = async () => {
      const categoriesResponse = await getEducationalCategoriesAdapter()

      if (!categoriesResponse.isOk) {
        return notify.error(categoriesResponse.message)
      }

      setCategories(categoriesResponse.payload)
    }

    loadData()
  }, [])

  const isReady = categories !== null

  return !isReady ? (
    <Spinner />
  ) : (
    <CollectiveOfferSummaryScreen
      offer={offer}
      categories={categories}
      reloadCollectiveOffer={reloadCollectiveOffer}
    />
  )
}

export default CollectiveOfferSummary
