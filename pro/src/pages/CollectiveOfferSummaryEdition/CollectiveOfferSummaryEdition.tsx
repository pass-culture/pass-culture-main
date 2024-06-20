import { AppLayout } from 'app/AppLayout'
import { canArchiveCollectiveOfferFromSummary } from 'components/ArchiveConfirmationModal/utils/canArchiveCollectiveOffer'
import { CollectiveOfferLayout } from 'components/CollectiveOfferLayout/CollectiveOfferLayout'
import { Mode } from 'core/OfferEducational/types'
import { CollectiveOfferSummaryEditionScreen } from 'screens/CollectiveOfferSummaryEdition/CollectiveOfferSummaryEdition'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'screens/OfferEducational/useCollectiveOfferFromParams'

const CollectiveOfferSummaryEdition = ({
  offer,
  isTemplate,
}: MandatoryCollectiveOfferFromParamsProps) => {
  return (
    <AppLayout layout={'sticky-actions'}>
      <CollectiveOfferLayout
        subTitle={offer.name}
        isTemplate={isTemplate}
        isArchivable={canArchiveCollectiveOfferFromSummary(offer)}
      >
        <CollectiveOfferSummaryEditionScreen
          offer={offer}
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
