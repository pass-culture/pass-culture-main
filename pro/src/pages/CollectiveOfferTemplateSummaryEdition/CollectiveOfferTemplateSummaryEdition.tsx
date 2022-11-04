import React, { useEffect, useState } from 'react'

import {
  getEducationalCategoriesAdapter,
  EducationalCategories,
  CollectiveOfferTemplate,
} from 'core/OfferEducational'
import useNotification from 'hooks/useNotification'
import CollectiveOfferSummaryEdition from 'screens/CollectiveOfferSummaryEdition'
import Spinner from 'ui-kit/Spinner/Spinner'

interface CollectiveOfferTemplateSummaryEditionProps {
  offer: CollectiveOfferTemplate
}

const CollectiveOfferTemplateSummaryEdition = ({
  offer,
}: CollectiveOfferTemplateSummaryEditionProps) => {
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
    <CollectiveOfferSummaryEdition offer={offer} categories={categories} />
  )
}

export default CollectiveOfferTemplateSummaryEdition
