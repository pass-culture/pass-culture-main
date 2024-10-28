import React from 'react'

import { Layout } from 'app/App/layout/Layout'
import { isCollectiveOffer } from 'commons/core/OfferEducational/types'
import { RouteLeavingGuardCollectiveOfferCreation } from 'components/RouteLeavingGuardCollectiveOfferCreation/RouteLeavingGuardCollectiveOfferCreation'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { CollectiveOfferLayout } from 'pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferLayout'

import { CollectiveOfferSummaryCreationScreen } from './CollectiveOfferSummaryCreationScreen'

export const CollectiveOfferSummaryCreation = ({
  offer,
  isTemplate,
}: MandatoryCollectiveOfferFromParamsProps) => {
  return (
    <Layout layout={'sticky-actions'}>
      <CollectiveOfferLayout
        subTitle={offer.name}
        isFromTemplate={isCollectiveOffer(offer) && Boolean(offer.templateId)}
        isTemplate={isTemplate}
        isCreation={true}
        offer={offer}
      >
        <CollectiveOfferSummaryCreationScreen offer={offer} />
        <RouteLeavingGuardCollectiveOfferCreation when={false} />
      </CollectiveOfferLayout>
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(
  CollectiveOfferSummaryCreation
)
