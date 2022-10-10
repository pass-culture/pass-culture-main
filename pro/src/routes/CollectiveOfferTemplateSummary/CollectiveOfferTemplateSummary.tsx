import React, { useEffect, useState } from 'react'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import {
  getEducationalCategoriesAdapter,
  EducationalCategories,
  CollectiveOfferTemplate,
} from 'core/OfferEducational'
import CollectiveOfferSummary from 'screens/CollectiveOfferSummary'

interface CollectiveOfferTemplateSummaryProps {
  offer: CollectiveOfferTemplate
}

const CollectiveOfferTemplateSummary = ({
  offer,
}: CollectiveOfferTemplateSummaryProps) => {
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

  const isReady = offer !== null && categories !== null

  return !isReady ? (
    <Spinner />
  ) : (
    <CollectiveOfferSummary offer={offer} categories={categories} />
  )
}

export default CollectiveOfferTemplateSummary
