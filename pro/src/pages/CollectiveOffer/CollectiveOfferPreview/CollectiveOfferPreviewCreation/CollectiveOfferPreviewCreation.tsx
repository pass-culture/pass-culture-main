import { AppLayout } from 'app/AppLayout'
import { isCollectiveOffer } from 'commons/core/OfferEducational/types'
import { CollectiveOfferLayout } from 'components/CollectiveOfferLayout/CollectiveOfferLayout'
import { RouteLeavingGuardCollectiveOfferCreation } from 'components/RouteLeavingGuardCollectiveOfferCreation/RouteLeavingGuardCollectiveOfferCreation'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { CollectiveOfferPreviewCreationScreen } from 'pages/CollectiveOffer/CollectiveOfferPreview/CollectiveOfferPreviewCreation/components/CollectiveOfferPreviewCreation/CollectiveOfferPreviewCreationScreen'

export const CollectiveOfferPreviewCreation = ({
  offer,
  isTemplate,
  offerer,
}: MandatoryCollectiveOfferFromParamsProps) => {
  return (
    <AppLayout layout={'sticky-actions'}>
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
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(
  CollectiveOfferPreviewCreation
)
