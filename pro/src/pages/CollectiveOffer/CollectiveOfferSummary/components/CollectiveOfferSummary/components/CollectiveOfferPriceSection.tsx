import type { GetCollectiveOfferTemplateResponseModel } from '@/apiClient/v1'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { SummaryDescriptionList } from '@/ui-kit/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from '@/ui-kit/SummaryLayout/SummarySubSection'

import { DEFAULT_RECAP_VALUE } from './constants'

interface CollectiveOfferPriceSectionProps {
  offer: GetCollectiveOfferTemplateResponseModel
}

export const CollectiveOfferPriceSection = ({
  offer,
}: CollectiveOfferPriceSectionProps) => {
  const isNewCollectivePriceEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS'
  )

  return (
    <SummarySubSection
      title="Prix"
      shouldShowDivider={!isNewCollectivePriceEnabled}
    >
      <SummaryDescriptionList
        descriptions={[{ text: offer.priceDetail || DEFAULT_RECAP_VALUE }]}
      />
    </SummarySubSection>
  )
}
