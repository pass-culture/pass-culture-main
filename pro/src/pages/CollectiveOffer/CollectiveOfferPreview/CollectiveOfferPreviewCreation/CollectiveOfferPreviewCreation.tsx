import { Layout } from 'app/App/layout/Layout'
import { isCollectiveOffer } from 'commons/core/OfferEducational/types'
import { RouteLeavingGuardCollectiveOfferCreation } from 'components/RouteLeavingGuardCollectiveOfferCreation/RouteLeavingGuardCollectiveOfferCreation'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { CollectiveOfferLayout } from 'pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferLayout'
import { CollectiveOfferPreviewCreationScreen } from 'pages/CollectiveOffer/CollectiveOfferPreview/CollectiveOfferPreviewCreation/components/CollectiveOfferPreviewCreation/CollectiveOfferPreviewCreationScreen'

export const CollectiveOfferPreviewCreation = ({
  offer,
  isTemplate,
  offerer,
}: MandatoryCollectiveOfferFromParamsProps) => {
  return (
    <Layout layout={'sticky-actions'}>
      <CollectiveOfferLayout
        subTitle={offer.name}
        isFromTemplate={isCollectiveOffer(offer) && Boolean(offer.templateId)}
        isTemplate={isTemplate}
        isCreation
        offer={offer}
      >
        <CollectiveOfferPreviewCreationScreen offer={offer} offerer={offerer} />
        <RouteLeavingGuardCollectiveOfferCreation when={false} />
      </CollectiveOfferLayout>
    </Layout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(
  CollectiveOfferPreviewCreation
)
