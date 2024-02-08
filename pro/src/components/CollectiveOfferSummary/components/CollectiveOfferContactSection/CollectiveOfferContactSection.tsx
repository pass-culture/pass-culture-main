import React from 'react'

import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'

interface CollectiveOfferContactSectionProps {
  phone?: string | null
  email: string
}

const CollectiveOfferContactSection = ({
  phone,
  email,
}: CollectiveOfferContactSectionProps) => {
  return (
    <SummarySubSection title="Contact">
      <SummaryDescriptionList
        descriptions={[
          { title: 'Téléphone', text: phone },
          { title: 'Email', text: email },
        ]}
      />
    </SummarySubSection>
  )
}

export default CollectiveOfferContactSection
