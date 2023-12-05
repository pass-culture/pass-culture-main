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
    <AppLayout>
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
          />
          <RouteLeavingGuardCollectiveOfferCreation />
        </CollectiveOfferLayout>
      )}
    </AppLayout>
  )
}

export default withCollectiveOfferFromParams(CollectiveOfferSummaryCreation)
