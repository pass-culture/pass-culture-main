import { AppLayout } from 'app/AppLayout'
import CollectiveOfferLayout from 'components/CollectiveOfferLayout'
import RouteLeavingGuardCollectiveOfferCreation from 'components/RouteLeavingGuardCollectiveOfferCreation'
import { isCollectiveOffer } from 'core/OfferEducational'
import CollectiveOfferPreviewCreationScreen from 'screens/CollectiveOfferPreviewCreation/CollectiveOfferPreviewCreation'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'screens/OfferEducational/useCollectiveOfferFromParams'

export const CollectiveOfferPreviewCreation = ({
  offer,
  setOffer,
  isTemplate,
}: MandatoryCollectiveOfferFromParamsProps) => {
  return (
    <AppLayout layout={'sticky-actions'}>
      <CollectiveOfferLayout
        subTitle={offer?.name}
        isFromTemplate={isCollectiveOffer(offer) && Boolean(offer.templateId)}
        isTemplate={isTemplate}
        isCreation={true}
      >
        <CollectiveOfferPreviewCreationScreen
          offer={offer}
          setOffer={setOffer}
        />
        <RouteLeavingGuardCollectiveOfferCreation />
      </CollectiveOfferLayout>
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(
  CollectiveOfferPreviewCreation
)
