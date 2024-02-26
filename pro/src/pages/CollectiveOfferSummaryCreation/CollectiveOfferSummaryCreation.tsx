import React from 'react'

import { AppLayout } from 'app/AppLayout'
import CollectiveOfferLayout from 'components/CollectiveOfferLayout'
import RouteLeavingGuardCollectiveOfferCreation from 'components/RouteLeavingGuardCollectiveOfferCreation'
import { isCollectiveOffer } from 'core/OfferEducational'
import CollectiveOfferSummaryCreationScreen from 'screens/CollectiveOfferSummaryCreation'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'screens/OfferEducational/useCollectiveOfferFromParams'

export const CollectiveOfferSummaryCreation = ({
  offer,
  setOffer,
  isTemplate,
  offerer,
}: MandatoryCollectiveOfferFromParamsProps) => {
  return (
    <AppLayout layout={'sticky-actions'}>
      <CollectiveOfferLayout
        subTitle={offer?.name}
        isFromTemplate={isCollectiveOffer(offer) && Boolean(offer.templateId)}
        isTemplate={isTemplate}
        isCreation={true}
      >
        <CollectiveOfferSummaryCreationScreen
          offer={offer}
          setOffer={setOffer}
          offerer={offerer}
        />
        <RouteLeavingGuardCollectiveOfferCreation />
      </CollectiveOfferLayout>
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(
  CollectiveOfferSummaryCreation
)
