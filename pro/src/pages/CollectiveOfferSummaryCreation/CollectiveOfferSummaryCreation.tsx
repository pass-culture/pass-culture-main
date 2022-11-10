import React from 'react'

import RouteLeavingGuardOfferCreation from 'components/RouteLeavingGuardOfferCreation'
import {
  getEducationalCategoriesAdapter,
  CollectiveOffer,
  CollectiveOfferTemplate,
} from 'core/OfferEducational'
import { useAdapter } from 'hooks'
import useNotification from 'hooks/useNotification'
import CollectiveOfferSummaryCreationScreen from 'screens/CollectiveOfferSummaryCreation'
import Spinner from 'ui-kit/Spinner/Spinner'

interface CollectiveOfferSummaryCreationProps {
  offer: CollectiveOffer | CollectiveOfferTemplate
  setOffer:
    | ((offer: CollectiveOffer) => void)
    | ((offer: CollectiveOfferTemplate) => void)
}

const CollectiveOfferSummaryCreation = ({
  offer,
  setOffer,
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
        setOffer={setOffer}
      />
      <RouteLeavingGuardOfferCreation />
    </>
  )
}

export default CollectiveOfferSummaryCreation
