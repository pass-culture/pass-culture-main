import type { GetCollectiveOfferTemplateResponseModel } from '@/apiClient/v1'
import { SummaryDescriptionList } from '@/ui-kit/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from '@/ui-kit/SummaryLayout/SummarySubSection'

import { DEFAULT_RECAP_VALUE } from './constants'

interface CollectiveOfferPriceSectionProps {
  offer: GetCollectiveOfferTemplateResponseModel
}

export const CollectiveOfferPriceSection = ({
  offer,
}: CollectiveOfferPriceSectionProps) => {
  return (
    <SummarySubSection title="Prix">
      <SummaryDescriptionList
        descriptions={[
          { text: offer.educationalPriceDetail || DEFAULT_RECAP_VALUE },
        ]}
      />
    </SummarySubSection>
  )
}
