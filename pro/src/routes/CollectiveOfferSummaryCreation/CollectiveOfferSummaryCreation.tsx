import React from 'react'

import Spinner from 'components/layout/Spinner'
import {
  getEducationalCategoriesAdapter,
  CollectiveOffer,
} from 'core/OfferEducational'
import { useAdapter } from 'hooks'
import useNotification from 'hooks/useNotification'
import CollectiveOfferSummaryCreationScreen from 'screens/CollectiveOfferSummaryCreation'

interface CollectiveOfferSummaryCreationProps {
  offer: CollectiveOffer
}

const CollectiveOfferSummaryCreation = ({
  offer,
}: CollectiveOfferSummaryCreationProps) => {
  const notify = useNotification()

  const {
    data: categories,
    error,
    isLoading,
  } = useAdapter(getEducationalCategoriesAdapter)

  if (error) {
    return notify.error(error.message)
  }

  return isLoading ? (
    <Spinner />
  ) : (
    <CollectiveOfferSummaryCreationScreen
      offer={offer}
      categories={categories}
    />
  )
}

export default CollectiveOfferSummaryCreation
