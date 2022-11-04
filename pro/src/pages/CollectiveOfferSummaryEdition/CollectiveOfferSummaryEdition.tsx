import React, { useEffect, useState } from 'react'

import {
  getEducationalCategoriesAdapter,
  EducationalCategories,
  CollectiveOffer,
} from 'core/OfferEducational'
import useNotification from 'hooks/useNotification'
import CollectiveOfferSummaryEditionScreen from 'screens/CollectiveOfferSummaryEdition'
import Spinner from 'ui-kit/Spinner/Spinner'

interface CollectiveOfferSummaryEditionProps {
  offer: CollectiveOffer
  reloadCollectiveOffer: () => void
}

const CollectiveOfferSummaryEdition = ({
  offer,
  reloadCollectiveOffer,
}: CollectiveOfferSummaryEditionProps) => {
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
    <CollectiveOfferSummaryEditionScreen
      offer={offer}
      categories={categories}
      reloadCollectiveOffer={reloadCollectiveOffer}
    />
  )
}

export default CollectiveOfferSummaryEdition
