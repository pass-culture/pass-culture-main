import React from 'react'

import {
  getEducationalCategoriesAdapter,
  CollectiveOffer,
  CollectiveOfferTemplate,
} from 'core/OfferEducational'
import { useAdapter } from 'hooks'
import useNotification from 'hooks/useNotification'
import RouteLeavingGuardOfferCreation from 'new_components/RouteLeavingGuardOfferCreation'
import CollectiveOfferSummaryCreationScreen from 'screens/CollectiveOfferSummaryCreation'
import Spinner from 'ui-kit/Spinner/Spinner'

interface CollectiveOfferSummaryCreationProps {
  offer: CollectiveOffer | CollectiveOfferTemplate
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
    notify.error(error.message)
    return <></>
  }

  return isLoading ? (
    <Spinner />
  ) : (
    <>
      <CollectiveOfferSummaryCreationScreen
        offer={offer}
        categories={categories}
      />
      <RouteLeavingGuardOfferCreation />
    </>
  )
}

export default CollectiveOfferSummaryCreation
