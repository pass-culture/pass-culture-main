import { AppLayout } from 'app/AppLayout'
import { Mode } from 'commons/core/OfferEducational/types'
import { canArchiveCollectiveOfferFromSummary } from 'components/ArchiveConfirmationModal/utils/canArchiveCollectiveOffer'
import { CollectiveOfferLayout } from 'components/CollectiveOfferLayout/CollectiveOfferLayout'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { CollectiveOfferSummaryEditionScreen } from 'pages/CollectiveOffer/CollectiveOfferSummary/CollectiveOfferSummaryEdition/components/CollectiveOfferSummaryEdition/CollectiveOfferSummaryEdition'

const CollectiveOfferSummaryEdition = ({
  offer,
  isTemplate,
}: MandatoryCollectiveOfferFromParamsProps) => {
  return (
    <AppLayout layout={'sticky-actions'}>
      <CollectiveOfferLayout
        subTitle={offer.name}
        isTemplate={isTemplate}
        offer={offer}
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
