import { AppLayout } from 'app/AppLayout'
import CollectiveOfferLayout from 'components/CollectiveOfferLayout'
import { Mode } from 'core/OfferEducational'
import { CollectiveOfferSummaryEditionScreen } from 'screens/CollectiveOfferSummaryEdition/CollectiveOfferSummaryEdition'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'screens/OfferEducational/useCollectiveOfferFromParams'

const CollectiveOfferSummaryEdition = ({
  offer,
  reloadCollectiveOffer,
  isTemplate,
}: MandatoryCollectiveOfferFromParamsProps) => {
  return (
    <AppLayout layout={'sticky-actions'}>
      <CollectiveOfferLayout subTitle={offer.name} isTemplate={isTemplate}>
        <CollectiveOfferSummaryEditionScreen
          offer={offer}
          reloadCollectiveOffer={reloadCollectiveOffer}
          mode={Mode.EDITION}
        />
      </CollectiveOfferLayout>
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(
  CollectiveOfferSummaryEdition
)
