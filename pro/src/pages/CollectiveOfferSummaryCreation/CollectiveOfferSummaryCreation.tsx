import React from 'react'

import { AppLayout } from 'app/AppLayout'
import CollectiveOfferLayout from 'components/CollectiveOfferLayout'
import RouteLeavingGuardCollectiveOfferCreation from 'components/RouteLeavingGuardCollectiveOfferCreation'
import {
  getEducationalCategoriesAdapter,
  isCollectiveOffer,
} from 'core/OfferEducational'
import { useAdapter } from 'hooks'
import useNotification from 'hooks/useNotification'
import CollectiveOfferSummaryCreationScreen from 'screens/CollectiveOfferSummaryCreation'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'screens/OfferEducational/useCollectiveOfferFromParams'
import Spinner from 'ui-kit/Spinner/Spinner'

export const CollectiveOfferSummaryCreation = ({
  offer,
  setOffer,
  isTemplate,
  offerer,
}: MandatoryCollectiveOfferFromParamsProps) => {
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

  return (
    <AppLayout layout={'sticky-actions'}>
      {isLoading ? (
        <Spinner />
      ) : (
        <CollectiveOfferLayout
          subTitle={offer?.name}
          isFromTemplate={isCollectiveOffer(offer) && Boolean(offer.templateId)}
          isTemplate={isTemplate}
          isCreation={true}
        >
          <CollectiveOfferSummaryCreationScreen
            offer={offer}
            categories={categories}
            setOffer={setOffer}
            offerer={offerer}
          />
          <RouteLeavingGuardCollectiveOfferCreation />
        </CollectiveOfferLayout>
      )}
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(
  CollectiveOfferSummaryCreation
)
