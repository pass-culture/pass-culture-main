import { Layout } from 'app/App/layout/Layout'
import { Mode } from 'commons/core/OfferEducational/types'
import {
  MandatoryCollectiveOfferFromParamsProps,
  withCollectiveOfferFromParams,
} from 'pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/useCollectiveOfferFromParams'
import { CollectiveOfferLayout } from 'pages/CollectiveOffer/CollectiveOfferLayout/CollectiveOfferLayout'
import { CollectiveOfferSummaryEditionScreen } from 'pages/CollectiveOffer/CollectiveOfferSummary/CollectiveOfferSummaryEdition/components/CollectiveOfferSummaryEdition/CollectiveOfferSummaryEdition'

const CollectiveOfferSummaryEdition = ({
  offer,
  isTemplate,
}: MandatoryCollectiveOfferFromParamsProps) => {
  return (
    <Layout layout={'sticky-actions'}>
      <CollectiveOfferLayout
        subTitle={offer.name}
        isTemplate={isTemplate}
        offer={offer}
      >
        <CollectiveOfferSummaryEditionScreen
          offer={offer}
          mode={Mode.EDITION}
        />
      </CollectiveOfferLayout>
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = withCollectiveOfferFromParams(
  CollectiveOfferSummaryEdition
)
